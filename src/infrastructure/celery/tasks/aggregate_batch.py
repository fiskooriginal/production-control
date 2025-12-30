import asyncio

from datetime import datetime
from uuid import UUID

from sqlalchemy.exc import DBAPIError, OperationalError

from src.core.logging import get_logger
from src.core.settings import CelerySettings
from src.core.time import datetime_now
from src.infrastructure.celery import states
from src.infrastructure.celery.app import celery_app, get_session_factory
from src.infrastructure.uow.unit_of_work import SqlAlchemyUnitOfWork

logger = get_logger("celery.tasks.aggregate_batch")

celery_settings = CelerySettings()


@celery_app.task(bind=True, max_retries=None)
def aggregate_batch(
    self,
    batch_id: str,
    unique_codes: list[str] | None = None,
    aggregated_at: str | None = None,
) -> dict:
    """
    Асинхронная массовая агрегация продукции.

    Используется когда нужно аггрегировать >100 единиц продукции.
    Возвращает результаты через task result backend.

    Args:
        batch_id: ID партии (UUID в виде строки)
        unique_codes: Список уникальных кодов продуктов для агрегации. Если None - агрегирует все продукты партии.
        aggregated_at: Время агрегации в формате ISO (если не указано, используется текущее)

    Returns:
        {
            "success": True,
            "total": 1000,
            "aggregated": 950,
            "failed": 50,
            "errors": [
                {"code": "ABC123", "reason": "already aggregated"},
                ...
            ]
        }
    """
    try:
        batch_uuid = UUID(batch_id)
    except ValueError as e:
        logger.error(f"Invalid batch_id format: {batch_id}")
        raise ValueError(f"Invalid batch_id format: {batch_id}") from e

    try:
        agg_at = None
        if aggregated_at:
            agg_at = datetime.fromisoformat(aggregated_at)
    except ValueError as e:
        logger.error(f"Invalid aggregated_at format: {aggregated_at}")
        raise ValueError(f"Invalid aggregated_at format: {aggregated_at}") from e

    return asyncio.run(_aggregate_batch_async(self, batch_uuid, unique_codes, agg_at))


def _is_retryable_error(exception: Exception) -> bool:
    """Проверяет, является ли ошибка повторяемой (retryable)"""
    return isinstance(exception, (OperationalError, DBAPIError))


async def _aggregate_batch_async(
    task_instance,
    batch_id: UUID,
    unique_codes: list[str] | None,
    aggregated_at: datetime | None,
) -> dict:
    """Асинхронная часть задачи агрегации"""
    session_factory = get_session_factory()

    total = 0
    aggregated_count = 0
    failed_count = 0
    errors: list[dict[str, str]] = []
    processed_codes: set[str] = set()

    try:
        async with session_factory() as session:
            uow = SqlAlchemyUnitOfWork(session)

            async with uow:
                batch = await uow.batches.get_or_raise(batch_id)

                if unique_codes:
                    requested_products = await uow.products.get_by_unique_codes(unique_codes)
                    found_codes_set = {p.unique_code.value for p in requested_products}

                    products_to_aggregate = []
                    for code in unique_codes:
                        if code not in found_codes_set:
                            errors.append({"code": code, "reason": "not found"})
                            failed_count += 1
                            processed_codes.add(code)

                    for product in requested_products:
                        if product.batch_id == batch_id:
                            products_to_aggregate.append(product)
                        else:
                            if product.unique_code.value not in processed_codes:
                                errors.append({"code": product.unique_code.value, "reason": "wrong batch"})
                                failed_count += 1
                                processed_codes.add(product.unique_code.value)

                    total = len(unique_codes)
                else:
                    products_to_aggregate = batch.products.copy()
                    total = len(products_to_aggregate)

                if aggregated_at is None:
                    aggregated_at = datetime_now()

                logger.info(f"Starting aggregation: batch_id={batch_id}, total={total}")

                products_before_aggregation = {p.uuid: p.is_aggregated for p in products_to_aggregate}

                products_for_aggregation = []
                for product in products_to_aggregate:
                    if product.is_aggregated:
                        if product.unique_code.value not in processed_codes:
                            errors.append({"code": product.unique_code.value, "reason": "already aggregated"})
                            failed_count += 1
                            processed_codes.add(product.unique_code.value)
                    else:
                        products_for_aggregation.append(product)

                if products_for_aggregation:
                    temp_products = batch.products
                    batch.products = products_for_aggregation
                    try:
                        batch.aggregate(aggregated_at)
                    finally:
                        batch.products = temp_products

                updated_products = []
                for idx, product in enumerate(products_to_aggregate, start=1):
                    was_aggregated_before = products_before_aggregation.get(product.uuid, False)

                    if product.is_aggregated and not was_aggregated_before:
                        aggregated_count += 1
                        updated_products.append(product)
                    elif not product.is_aggregated and not was_aggregated_before:
                        if product.unique_code.value not in processed_codes:
                            errors.append({"code": product.unique_code.value, "reason": "aggregation failed"})
                            failed_count += 1
                            processed_codes.add(product.unique_code.value)

                    if idx % max(1, total // 10) == 0 or idx == total:
                        progress = int((idx / total) * 100) if total > 0 else 0
                        task_instance.update_state(
                            state=states.PROGRESS,
                            meta={
                                "current": idx,
                                "total": total,
                                "progress": progress,
                            },
                        )

                for product in updated_products:
                    await uow.products.update(product)

                await uow.batches.update(batch)
                await uow.commit()

                if total > 0:
                    progress = 100
                    task_instance.update_state(
                        state=states.PROGRESS,
                        meta={
                            "current": total,
                            "total": total,
                            "progress": progress,
                        },
                    )

        logger.info(
            f"Aggregation completed: batch_id={batch_id}, total={total}, "
            f"aggregated={aggregated_count}, failed={failed_count}"
        )

        return {
            "success": True,
            "total": total,
            "aggregated": aggregated_count,
            "failed": failed_count,
            "errors": errors,
        }

    except Exception as e:
        logger.exception(f"Failed to aggregate batch {batch_id}: {e}")
        if _is_retryable_error(e) and task_instance.request.retries < celery_settings.task_max_retries:
            raise task_instance.retry(
                exc=e,
                countdown=celery_settings.task_default_retry_delay,
            ) from e
        raise
