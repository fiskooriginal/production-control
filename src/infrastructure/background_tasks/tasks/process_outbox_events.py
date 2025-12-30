import inspect

from sqlalchemy.exc import DBAPIError, OperationalError

from src.core.logging import get_logger
from src.core.settings import CelerySettings
from src.infrastructure.background_tasks.app import celery_app, get_session_factory, run_async_task
from src.infrastructure.events import EventSerializer
from src.infrastructure.events.handlers.registry import EventHandlerRegistry
from src.infrastructure.persistence.repositories.outbox import OutboxRepository

logger = get_logger("celery.tasks.process_outbox_events")

celery_settings = CelerySettings()


def _is_retryable_error(exception: Exception) -> bool:
    """Проверяет, является ли ошибка повторяемой (retryable)"""
    return isinstance(exception, (OperationalError, DBAPIError))


@celery_app.task(bind=True, max_retries=None, name="tasks.process_outbox_events")
def process_outbox_events(self) -> dict:
    """
    Обрабатывает pending события из Transactional Outbox.

    Захватывает события со статусом PENDING, десериализует их,
    вызывает зарегистрированные обработчики и обновляет статус событий.

    Returns:
        {
            "success": True,
            "processed": 10,
            "failed": 2,
            "total": 12
        }
    """
    return run_async_task(_process_outbox_events_async(self))


async def _process_outbox_events_async(task_instance) -> dict:
    """Асинхронная часть задачи обработки outbox событий"""
    session_factory = get_session_factory()

    processed_count = 0
    failed_count = 0

    try:
        async with session_factory() as session:
            outbox_repo = OutboxRepository(session)

            logger.info("Starting outbox events processing")

            events = await outbox_repo.claim_pending_events(limit=100, lock_duration_seconds=300)

            if not events:
                logger.debug("No pending events to process")
                return {
                    "success": True,
                    "processed": 0,
                    "failed": 0,
                    "total": 0,
                }

            logger.info(f"Claimed {len(events)} events for processing")

            for outbox_event in events:
                try:
                    await _process_single_event(outbox_event, outbox_repo, session)
                    processed_count += 1
                    logger.debug(f"Successfully processed event {outbox_event.uuid}")
                except Exception as e:
                    failed_count += 1
                    error_message = str(e)
                    logger.exception(
                        f"Failed to process event {outbox_event.uuid}: {error_message}",
                        extra={"event_id": str(outbox_event.uuid), "event_name": outbox_event.event_name},
                    )

                    try:
                        await outbox_repo.mark_event_failed(outbox_event.uuid, error_message)
                        await session.commit()
                    except Exception as commit_error:
                        logger.exception(
                            f"Failed to mark event {outbox_event.uuid} as failed: {commit_error}",
                            extra={"event_id": str(outbox_event.uuid)},
                        )
                        await session.rollback()

            logger.info(
                f"Outbox events processing completed: processed={processed_count}, failed={failed_count}, total={len(events)}"
            )

            return {
                "success": True,
                "processed": processed_count,
                "failed": failed_count,
                "total": len(events),
            }

    except Exception as e:
        logger.exception(f"Failed to process outbox events: {e}")
        if _is_retryable_error(e) and task_instance.request.retries < celery_settings.task_max_retries:
            raise task_instance.retry(
                exc=e,
                countdown=celery_settings.task_default_retry_delay,
            ) from e
        raise


async def _process_single_event(
    outbox_event,
    outbox_repo: OutboxRepository,
    session,
) -> None:
    """
    Обрабатывает одно событие из outbox.

    Args:
        outbox_event: OutboxEvent из БД
        outbox_repo: OutboxRepository для обновления статуса
        session: AsyncSession для транзакции
    """
    event_data = {
        "event_name": outbox_event.event_name,
        "event_version": outbox_event.event_version,
        "aggregate_id": str(outbox_event.aggregate_id),
        "occurred_at": outbox_event.occurred_at.isoformat(),
        "payload": outbox_event.payload,
    }

    deserialized_event = EventSerializer.deserialize(event_data)

    event_type = type(deserialized_event)
    handlers = EventHandlerRegistry.get_handlers(event_type)

    if not handlers:
        error_message = f"No handlers registered for event type {event_type.__name__}"
        logger.warning(
            f"{error_message} (event_id={outbox_event.uuid})",
            extra={"event_id": str(outbox_event.uuid), "event_type": event_type.__name__},
        )
        await outbox_repo.mark_event_failed(outbox_event.uuid, error_message)
        await session.commit()
        return

    for handler in handlers:
        try:
            if not hasattr(handler, "handle"):
                raise ValueError(f"Handler {type(handler).__name__} does not have handle method")

            if not callable(handler.handle):
                raise ValueError(f"Handler {type(handler).__name__} does not have callable handle method")

            if inspect.iscoroutinefunction(handler.handle):
                await handler.handle(deserialized_event)
            else:
                handler.handle(deserialized_event)
        except Exception as e:
            logger.exception(
                f"Handler {type(handler).__name__} failed for event {outbox_event.uuid}: {e}",
                extra={"event_id": str(outbox_event.uuid), "handler": type(handler).__name__},
            )
            raise

    await outbox_repo.mark_event_done(outbox_event.uuid)
    await session.commit()
