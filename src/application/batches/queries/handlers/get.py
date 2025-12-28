from uuid import UUID

from src.application.batches.queries.dtos import BatchReadDTO
from src.application.batches.queries.service import BatchQueryServiceProtocol
from src.core.logging import get_logger
from src.domain.common.exceptions import DoesNotExistError

logger = get_logger("query.handler.batches")


class GetBatchQueryHandler:
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
