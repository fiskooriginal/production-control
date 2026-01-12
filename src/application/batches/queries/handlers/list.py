from src.application.batches.queries.queries import ListBatchesQuery
from src.application.batches.queries.service import BatchQueryServiceProtocol
from src.core.logging import get_logger
from src.domain.batches import BatchEntity
from src.domain.common.queries import QueryResult

logger = get_logger("query.handler.batches")


class ListBatchesQueryHandler:
    def __init__(self, query_service: BatchQueryServiceProtocol):
        self._query_service = query_service

    async def execute(self, query: ListBatchesQuery) -> QueryResult[BatchEntity]:
        """Получает список партий с фильтрацией, пагинацией и сортировкой"""
        logger.debug(f"Listing batches: filters={query.filters}")
        try:
            result = await self._query_service.list(query)
            logger.debug(f"Listed {result.total} batches")
            return result
        except Exception as e:
            logger.exception(f"Failed to list batches: {e}")
            raise
