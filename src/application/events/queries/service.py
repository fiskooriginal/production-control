from typing import Protocol

from src.application.events.queries.dtos import EventTypeReadDTO


class EventTypeQueryServiceProtocol(Protocol):
    """Протокол Query Service для EventType (read-only операции)"""

    async def list_all(self) -> list[EventTypeReadDTO]:
        """Получает список всех типов событий"""
        ...
