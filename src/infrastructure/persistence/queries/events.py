from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.events.queries.dtos import EventTypeReadDTO
from src.application.events.queries.service import EventTypeQueryServiceProtocol
from src.infrastructure.common.exceptions import DatabaseException
from src.infrastructure.persistence.models.event_type import EventType


class EventTypeQueryService(EventTypeQueryServiceProtocol):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_all(self) -> list[EventTypeReadDTO]:
        """Получает список всех типов событий"""
        try:
            stmt = select(EventType).order_by(EventType.name, EventType.version)
            result = await self._session.execute(stmt)
            event_types = result.scalars().all()

            return [
                EventTypeReadDTO(
                    uuid=et.uuid,
                    created_at=et.created_at,
                    updated_at=et.updated_at,
                    name=et.name,
                    version=et.version,
                    webhook_enabled=et.webhook_enabled,
                    description=et.description,
                )
                for et in event_types
            ]
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении списка типов событий: {e}") from e
