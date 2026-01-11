from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.time import datetime_now
from src.domain.common.enums import EventTypesEnum
from src.infrastructure.common.exceptions import DatabaseException
from src.infrastructure.persistence.models.event_type import EventType


class EventTypeRepository:
    """Репозиторий для работы с типами событий"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_name(self, name: str, version: int) -> EventType | None:
        """Получает тип события по имени и версии"""
        try:
            stmt = select(EventType).where(EventType.name == name, EventType.version == version)
            result = await self._session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении типа события: {e}") from e

    async def get_by_event_type(self, event_type: EventTypesEnum, version: int = 1) -> EventType | None:
        """Получает тип события по EventTypesEnum и версии"""
        return await self.get_by_name(str(event_type), version)

    async def get_or_create(self, name: str, version: int, webhook_enabled: bool = True) -> EventType:
        """Получает тип события или создает новый, если не существует"""
        try:
            event_type = await self.get_by_name(name, version)
            if event_type is None:
                event_type = EventType(
                    created_at=datetime_now(naive=True),
                    name=name,
                    version=version,
                    webhook_enabled=webhook_enabled,
                )
                self._session.add(event_type)
                await self._session.flush()
            return event_type
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении/создании типа события: {e}") from e

    async def list(self, webhook_enabled: bool | None = None) -> list[EventType]:
        """Получает список типов событий, опционально отфильтрованный по webhook_enabled"""
        try:
            stmt = select(EventType)
            if webhook_enabled is not None:
                stmt = stmt.where(EventType.webhook_enabled == webhook_enabled)
            stmt = stmt.order_by(EventType.name, EventType.version)
            result = await self._session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении списка типов событий: {e}") from e

    async def update_webhook_enabled(self, event_type_id: UUID, enabled: bool) -> EventType:
        """Обновляет флаг webhook_enabled для типа события"""
        try:
            event_type = await self._session.get(EventType, event_type_id)
            if event_type is None:
                raise ValueError(f"Тип события с UUID {event_type_id} не найден")

            event_type.webhook_enabled = enabled
            event_type.updated_at = datetime_now(naive=True)
            await self._session.flush()
            return event_type
        except ValueError:
            raise
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при обновлении типа события: {e}") from e
