from src.core.logging import get_logger
from src.domain.batches.events import BatchClosedEvent
from src.infrastructure.background_tasks.di.reports import get_batch_closed_handler
from src.infrastructure.events.handlers.registry import EventHandlerRegistry

logger = get_logger("events.handlers.setup")


def setup_event_handlers() -> None:
    """
    Регистрирует все event handlers в EventHandlerRegistry.
    Вызывается при старте Celery worker.

    Импортирует модули с хендлерами для активации декораторов @event_handler,
    затем создает экземпляры хендлеров через DI функции и регистрирует их.
    """
    from src.application.batches.reports.handlers import GenerateReportOnBatchClosedHandler  # noqa: F401

    handler = get_batch_closed_handler()
    EventHandlerRegistry.register(BatchClosedEvent, handler)
    logger.info(f"Registered BatchClosedEvent handler: {type(handler).__name__}")

    registered_count = sum(len(handlers) for handlers in EventHandlerRegistry._handlers.values())
    logger.info(f"Event handlers setup completed: {registered_count} handler(s) registered")
