from datetime import date, datetime
from typing import Any
from uuid import UUID

from src.application.events.registry import EventRegistry
from src.domain.batches.value_objects import BatchNumber
from src.domain.shared.events import DomainEvent


class EventSerializer:
    """
    Сериализует/десериализует доменные события для хранения в outbox.
    Использует стабильные event_name + event_version из EventRegistry.
    """

    @staticmethod
    def serialize(event: DomainEvent) -> dict[str, Any]:
        """
        Сериализует доменное событие в JSON-safe словарь.
        UUID/datetime/ValueObjects → строки/числа.
        """
        if not EventRegistry.is_registered(type(event)):
            raise ValueError(f"Event {type(event).__name__} is not registered in EventRegistry")

        event_name, event_version = EventRegistry.get_event_metadata(type(event))

        payload = {}
        for field_name, field_value in event.__dict__.items():
            if field_name in ("occurred_at", "aggregate_id"):
                continue
            payload[field_name] = EventSerializer._serialize_value(field_value)

        return {
            "event_name": event_name,
            "event_version": event_version,
            "aggregate_id": str(event.aggregate_id),
            "occurred_at": event.occurred_at.isoformat(),
            "payload": payload,
        }

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        """Сериализует значение в JSON-safe тип"""
        if isinstance(value, UUID):
            return str(value)
        elif isinstance(value, (datetime, date)):
            return value.isoformat()
        elif isinstance(value, BatchNumber) or hasattr(value, "value"):
            return value.value
        elif isinstance(value, (str, int, float, bool, type(None))):
            return value
        elif isinstance(value, (list, tuple)):
            return [EventSerializer._serialize_value(v) for v in value]
        elif isinstance(value, dict):
            return {k: EventSerializer._serialize_value(v) for k, v in value.items()}
        else:
            return str(value)

    @staticmethod
    def deserialize(data: dict[str, Any]) -> DomainEvent:
        """
        Десериализует событие из словаря (для будущего воркера).
        Пока базовая реализация - можно расширить по мере необходимости.
        """
        event_name = data["event_name"]
        event_version = data["event_version"]
        event_class = EventRegistry.get_event_class(event_name, event_version)

        payload = data["payload"].copy()
        payload["aggregate_id"] = UUID(data["aggregate_id"])
        payload["occurred_at"] = datetime.fromisoformat(data["occurred_at"])

        return event_class(**payload)
