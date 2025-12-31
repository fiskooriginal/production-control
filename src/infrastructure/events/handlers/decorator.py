from collections.abc import Callable
from typing import Any, TypeVar

from src.domain.common.events import DomainEvent
from src.infrastructure.events.handlers.registry import EventHandlerRegistry

T = TypeVar("T", bound=DomainEvent)


def event_handler[T](event_type: type[T]) -> Callable[[Any], Any]:
    """¬
    Декоратор для автоматической регистрации обработчиков событий.

    Поддерживает как классы, так и функции-хендлеры.
    Позволяет регистрировать несколько хендлеров для одного события.

    Args:
        event_type: Тип доменного события, которое обрабатывает хендлер

    Example:
        @event_handler(BatchClosedEvent)
        class GenerateReportOnBatchClosedHandler:
            async def handle(self, event: BatchClosedEvent) -> None:
                ...

        @event_handler(BatchClosedEvent)
        async def another_handler(event: BatchClosedEvent) -> None:
            ...
    """

    def decorator(handler: Any) -> Any:
        """Регистрирует хендлер в EventHandlerRegistry."""
        EventHandlerRegistry.register(event_type, handler)
        return handler

    return decorator
