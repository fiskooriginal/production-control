from typing import ClassVar, TypeVar

from src.domain.batches.events import (
    BatchClosedEvent,
    BatchCreatedEvent,
    ProductAddedToBatchEvent,
    ProductRemovedFromBatchEvent,
)
from src.domain.products.events import ProductAggregatedEvent
from src.domain.shared.events import DomainEvent

T = TypeVar("T", bound=DomainEvent)


class EventRegistry:
    """
    Whitelist-реестр доменных событий для стабильной (де)сериализации.
    Использует event_name + event_version вместо полных путей классов.
    """

    _registry: ClassVar[dict[tuple[str, int], type[DomainEvent]]] = {}
    _reverse_registry: ClassVar[dict[type[DomainEvent], tuple[str, int]]] = {}

    @classmethod
    def register(cls, event_name: str, event_version: int, event_class: type[DomainEvent]) -> None:
        """Регистрирует тип события в whitelist"""
        key = (event_name, event_version)
        if key in cls._registry:
            raise ValueError(f"Event {event_name} v{event_version} already registered")
        cls._registry[key] = event_class
        cls._reverse_registry[event_class] = key

    @classmethod
    def get_event_class(cls, event_name: str, event_version: int) -> type[DomainEvent]:
        """Получает класс события по имени и версии"""
        key = (event_name, event_version)
        if key not in cls._registry:
            raise ValueError(f"Event {event_name} v{event_version} not registered")
        return cls._registry[key]

    @classmethod
    def get_event_metadata(cls, event_class: type[DomainEvent]) -> tuple[str, int]:
        """Получает имя и версию события по классу"""
        if event_class not in cls._reverse_registry:
            raise ValueError(f"Event class {event_class.__name__} not registered")
        return cls._reverse_registry[event_class]

    @classmethod
    def is_registered(cls, event_class: type[DomainEvent]) -> bool:
        """Проверяет, зарегистрирован ли класс события"""
        return event_class in cls._reverse_registry


def _initialize_registry() -> None:
    """Инициализирует реестр всех доменных событий системы"""
    EventRegistry.register("batch.created", 1, BatchCreatedEvent)
    EventRegistry.register("batch.closed", 1, BatchClosedEvent)
    EventRegistry.register("batch.product_added", 1, ProductAddedToBatchEvent)
    EventRegistry.register("batch.product_removed", 1, ProductRemovedFromBatchEvent)
    EventRegistry.register("product.aggregated", 1, ProductAggregatedEvent)


_initialize_registry()
