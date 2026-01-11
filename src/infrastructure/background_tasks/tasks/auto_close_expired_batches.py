from sqlalchemy.exc import DBAPIError, OperationalError

from src.application.batches.commands.aggregate import AggregateBatchCommand
from src.application.batches.commands.close import CloseBatchCommand
from src.application.batches.dtos.aggregate import AggregateBatchInputDTO
from src.application.batches.dtos.close import CloseBatchInputDTO
from src.core.logging import get_logger
from src.core.settings import CelerySettings
from src.core.time import datetime_now
from src.domain.common.exceptions import InvalidStateError
from src.infrastructure.background_tasks.app import celery_app, get_session_factory, run_async_task
from src.infrastructure.common.uow.unit_of_work import SqlAlchemyUnitOfWork

logger = get_logger("celery.tasks.auto_close_expired_batches")

celery_settings = CelerySettings()


@celery_app.task(bind=True, max_retries=None)
def auto_close_expired_batches(self) -> dict:
    """
    Закрывает партии, у которых shift_end < now().

    Запускается: каждый день в 01:00
    """
    return run_async_task(_auto_close_expired_batches_async(self))


def _is_retryable_error(exception: Exception) -> bool:
    """Проверяет, является ли ошибка повторяемой (retryable)"""
    return isinstance(exception, (OperationalError, DBAPIError))


async def _auto_close_expired_batches_async(task_instance) -> dict:
    """Асинхронная часть задачи автоматического закрытия просроченных партий"""
    session_factory = get_session_factory()

    closed_count = 0
    skipped_count = 0
    error_count = 0
    errors: list[dict[str, str]] = []

    try:
        now = datetime_now()

        async with session_factory() as session:
            uow = SqlAlchemyUnitOfWork(session)

            async with uow:
                expired_batches = await uow.batches.get_expired_open_batches(now)

                total = len(expired_batches)
                logger.info(f"Found {total} expired open batch(es)")

                if total == 0:
                    return {"success": True, "total": 0, "closed": 0, "skipped": 0, "errors": []}

                for batch in expired_batches:
                    try:
                        aggregate_command = AggregateBatchCommand(uow)
                        await aggregate_command.execute(AggregateBatchInputDTO(batch_id=batch.uuid))

                        close_command = CloseBatchCommand(uow)
                        await close_command.execute(CloseBatchInputDTO(batch_id=batch.uuid, closed_at=now))

                        closed_count += 1
                        logger.info(
                            f"Closed expired batch: batch_id={batch.uuid}, batch_number={batch.batch_number.value}"
                        )

                    except InvalidStateError as e:
                        skipped_count += 1
                        logger.warning(
                            f"Cannot close batch {batch.uuid} (batch_number={batch.batch_number.value}): {e}. Skipping."
                        )
                        errors.append({"batch_id": str(batch.uuid), "reason": str(e)})

                    except Exception as e:
                        error_count += 1
                        logger.exception(f"Failed to close batch {batch.uuid}: {e}")
                        errors.append({"batch_id": str(batch.uuid), "reason": f"Unexpected error: {e!s}"})

        logger.info(
            f"Auto-close completed: total={total}, closed={closed_count}, skipped={skipped_count}, errors={error_count}"
        )

        return {
            "success": True,
            "total": total,
            "closed": closed_count,
            "skipped": skipped_count,
            "errors": errors,
        }

    except Exception as e:
        logger.exception(f"Failed to auto-close expired batches: {e}")
        if _is_retryable_error(e) and task_instance.request.retries < celery_settings.task_max_retries:
            raise task_instance.retry(
                exc=e,
                countdown=celery_settings.task_default_retry_delay,
            ) from e
        raise
