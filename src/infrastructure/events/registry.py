from typing import ClassVar, TypeVar

from src.domain.batches.events import (
    BatchAggregatedEvent,
    BatchClosedEvent,
    BatchCreatedEvent,
    BatchDeletedEvent,
    BatchOpenedEvent,
    BatchUpdatedEvent,
    ProductAddedToBatchEvent,
    ProductRemovedFromBatchEvent,
)
from src.domain.batches.events.import_completed import BatchesImportCompletedEvent
from src.domain.batches.events.report_generated import ReportGeneratedEvent
from src.domain.common.enums import EventTypesEnum
from src.domain.common.events import DomainEvent
from src.domain.products.events import ProductAggregatedEvent
from src.domain.work_centers.events import WorkCenterDeletedEvent

T = TypeVar("T", bound=DomainEvent)


class EventRegistry:
    """
    Whitelist-реестр доменных событий для стабильной (де)сериализации.
    Использует event_name + event_version вместо полных путей классов.
    """

    _registry: ClassVar[dict[tuple[str, int], type[DomainEvent]]] = {}
    _reverse_registry: ClassVar[dict[type[DomainEvent], tuple[str, int]]] = {}

    @classmethod
    def register(cls, event_type: EventTypesEnum, event_version: int, event_class: type[DomainEvent]) -> None:
        """Регистрирует тип события в whitelist"""
        event_name = str(event_type)
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
    def get_event_name(cls, event_type: EventTypesEnum) -> str:
        """Получает строковое имя события из EventTypesEnum"""
        return str(event_type)

    @classmethod
    def is_registered(cls, event_class: type[DomainEvent]) -> bool:
        """Проверяет, зарегистрирован ли класс события"""
        return event_class in cls._reverse_registry

    @classmethod
    def get_all_registered(cls) -> list[tuple[str, int]]:
        """Получает список всех зарегистрированных событий (имя, версия)"""
        return list(cls._registry.keys())


def _initialize_registry() -> None:
    """Инициализирует реестр всех доменных событий системы"""
    EventRegistry.register(EventTypesEnum.BATCH_CREATED, 1, BatchCreatedEvent)
    EventRegistry.register(EventTypesEnum.BATCH_CLOSED, 1, BatchClosedEvent)
    EventRegistry.register(EventTypesEnum.BATCH_OPENED, 1, BatchOpenedEvent)
    EventRegistry.register(EventTypesEnum.BATCH_UPDATED, 1, BatchUpdatedEvent)
    EventRegistry.register(EventTypesEnum.BATCH_PRODUCT_ADDED, 1, ProductAddedToBatchEvent)
    EventRegistry.register(EventTypesEnum.BATCH_PRODUCT_REMOVED, 1, ProductRemovedFromBatchEvent)
    EventRegistry.register(EventTypesEnum.BATCH_AGGREGATED, 1, BatchAggregatedEvent)
    EventRegistry.register(EventTypesEnum.BATCH_DELETED, 1, BatchDeletedEvent)
    EventRegistry.register(EventTypesEnum.BATCH_REPORT_GENERATED, 1, ReportGeneratedEvent)
    EventRegistry.register(EventTypesEnum.PRODUCT_AGGREGATED, 1, ProductAggregatedEvent)
    EventRegistry.register(EventTypesEnum.WORK_CENTER_DELETED, 1, WorkCenterDeletedEvent)
    EventRegistry.register(EventTypesEnum.BATCH_IMPORT_COMPLETED, 1, BatchesImportCompletedEvent)


_initialize_registry()
