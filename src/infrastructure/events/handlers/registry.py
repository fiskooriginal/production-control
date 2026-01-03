from typing import ClassVar, TypeVar

from src.application.batches.events.handlers import BatchClosedHandler
from src.application.work_centers.events.handlers.work_center_deleted_handler import WorkCenterDeletedHandler
from src.domain.batches.events import BatchClosedEvent
from src.domain.common.events import DomainEvent
from src.domain.work_centers.events import WorkCenterDeletedEvent

T = TypeVar("T", bound=DomainEvent)


class EventHandlerRegistry:
    """
    Реестр обработчиков событий для Outbox Worker.
    Позволяет регистрировать обработчики для типов доменных событий.
    """

    _handlers: ClassVar[dict[type[DomainEvent], list]] = {}

    @classmethod
    def register(cls, event_type: type[DomainEvent], handler) -> None:
        """
        Регистрирует обработчик для типа события.

        Args:
            event_type: Тип доменного события
            handler: Обработчик события (должен иметь метод handle(event))
        """
        if event_type not in cls._handlers:
            cls._handlers[event_type] = []

        cls._handlers[event_type].append(handler)

    @classmethod
    def get_handlers(cls, event_type: type[DomainEvent]) -> list:
        """
        Возвращает все обработчики для типа события.

        Args:
            event_type: Тип доменного события

        Returns:
            Список обработчиков для данного типа события
        """
        return cls._handlers.get(event_type, [])

    @classmethod
    def clear(cls) -> None:
        """
        Очищает реестр обработчиков.
        Используется в тестах.
        """
        cls._handlers.clear()


def _initialize_registry() -> None:
    """Инициализирует реестр всех обработчиков событий системы"""
    EventHandlerRegistry.register(BatchClosedEvent, BatchClosedHandler)
    EventHandlerRegistry.register(WorkCenterDeletedEvent, WorkCenterDeletedHandler)


_initialize_registry()
