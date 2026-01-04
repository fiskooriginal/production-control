from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logging import get_logger
from src.infrastructure.events.registry import EventRegistry
from src.infrastructure.persistence.repositories.event_type import EventTypeRepository

logger = get_logger("events.sync")


class EventTypeSyncService:
    """Сервис синхронизации событий из EventRegistry в БД"""

    def __init__(self, session: AsyncSession):
        self._session = session
        self._repository = EventTypeRepository(session)

    async def sync(self) -> None:
        """Синхронизирует события из EventRegistry в БД"""
        logger.info("Начало синхронизации типов событий из EventRegistry в БД")

        registered_events = EventRegistry.get_all_registered()

        logger.debug(f"Найдено {len(registered_events)} зарегистрированных событий в EventRegistry")

        for event_name, event_version in registered_events:
            try:
                await self._repository.get_or_create(name=event_name, version=event_version)
                logger.debug(f"Создан новый тип события: {event_name} v{event_version}")
            except Exception as e:
                logger.exception(f"Ошибка при синхронизации события {event_name} v{event_version}: {e}")
                raise
