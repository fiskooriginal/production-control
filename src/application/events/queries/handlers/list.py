from src.application.events.queries.dtos import EventTypeReadDTO
from src.application.events.queries.service import EventTypeQueryServiceProtocol
from src.core.logging import get_logger

logger = get_logger("query.handler.events")


class ListEventsQueryHandler:
    def __init__(self, query_service: EventTypeQueryServiceProtocol):
        self._query_service = query_service

    async def execute(self) -> list[EventTypeReadDTO]:
        """Получает список всех типов событий"""
        logger.debug("Listing all event types")
        try:
            result = await self._query_service.list_all()
            logger.debug(f"Listed {len(result)} event types")
            return result
        except Exception as e:
            logger.exception(f"Failed to list event types: {e}")
            raise
