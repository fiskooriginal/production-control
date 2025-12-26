from uuid import UUID

from src.application.queries.batches import BatchReadDTO, ListBatchesQuery
from src.application.queries.ports import BatchQueryServiceProtocol
from src.core.logging import get_logger
from src.domain.common.exceptions import DoesNotExistError
from src.domain.common.queries import QueryResult

logger = get_logger("use_case.queries.batches")


class GetBatchQueryUseCase:
    def __init__(self, query_service: BatchQueryServiceProtocol):
        self._query_service = query_service

    async def execute(self, batch_id: UUID) -> BatchReadDTO:
        """Получает партию по UUID"""
        logger.debug(f"Getting batch: batch_id={batch_id}")
        try:
            result = await self._query_service.get(batch_id)
            if result is None:
                raise DoesNotExistError(f"Партия с UUID {batch_id} не найдена")
            logger.debug(f"Batch retrieved: batch_id={batch_id}")
            return result
        except DoesNotExistError:
            raise
        except Exception as e:
            logger.exception(f"Failed to get batch: {e}")
            raise


class ListBatchesQueryUseCase:
    def __init__(self, query_service: BatchQueryServiceProtocol):
        self._query_service = query_service

    async def execute(self, query: ListBatchesQuery) -> QueryResult[BatchReadDTO]:
        """Получает список партий с фильтрацией, пагинацией и сортировкой"""
        logger.debug(f"Listing batches: filters={query.filters}")
        try:
            result = await self._query_service.list(query)
            logger.debug(f"Listed {result.total} batches")
            return result
        except Exception as e:
            logger.exception(f"Failed to list batches: {e}")
            raise
