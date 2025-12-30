from src.core.logging import get_logger
from src.infrastructure.events.handlers.registry import EventHandlerRegistry

logger = get_logger("events.handlers.setup")


def setup_event_handlers() -> None:
    """
    Регистрирует все event handlers в EventHandlerRegistry.
    Вызывается при старте Celery worker.
    """

    # Пример регистрации:
    #
    # from src.domain.batches.events import BatchClosedEvent
    # from src.application.batches.reports.handlers.batch_closed_handler import (
    #     GenerateReportOnBatchClosedHandler
    # )
    # from src.presentation.di.reports import get_report_generation_service
    #
    # # Создаем зависимости (нужно будет создать DI функции)
    # report_service = get_report_generation_service()
    #
    # # Создаем и регистрируем обработчик
    # handler = GenerateReportOnBatchClosedHandler(report_service)
    # EventHandlerRegistry.register(BatchClosedEvent, handler)
    #
    # # Можно зарегистрировать несколько обработчиков для одного события:
    # another_handler = AnotherBatchClosedHandler(another_service)
    # EventHandlerRegistry.register(BatchClosedEvent, another_handler)

    registered_count = sum(len(handlers) for handlers in EventHandlerRegistry._handlers.values())
    logger.info(f"Event handlers setup completed: {registered_count} handler(s) registered")
