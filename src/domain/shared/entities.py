from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from src.domain.shared.events import DomainEvent
from src.domain.shared.time import utc_now


@dataclass(slots=True, kw_only=True)
class BaseEntity:
    uuid: UUID = field(default_factory=uuid4)

    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime | None = None
    _domain_events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def add_domain_event(self, event: DomainEvent) -> None:
        """Добавляет доменное событие"""
        if not hasattr(self, "_domain_events") or self._domain_events is None:
            self._domain_events = []
        self._domain_events.append(event)

    def get_domain_events(self) -> list[DomainEvent]:
        """Возвращает список доменных событий"""
        return getattr(self, "_domain_events", [])

    def clear_domain_events(self) -> None:
        """Очищает список доменных событий"""
        self._domain_events = []
