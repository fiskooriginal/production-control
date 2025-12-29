from uuid import UUID

from src.application.batches.dtos import AggregateBatchInputDTO
from src.application.common.cache.interface.protocol import CacheServiceProtocol
from src.application.common.cache.keys import get_batch_key, get_batches_list_pattern
from src.application.common.uow import UnitOfWorkProtocol
from src.core.logging import get_logger
from src.domain.batches.entities import BatchEntity
from src.domain.common.exceptions import InvalidStateError

logger = get_logger("command.batches")


class AggregateBatchCommand:
    def __init__(self, uow: UnitOfWorkProtocol, cache_service: CacheServiceProtocol | None = None):
        self._uow = uow
        self._cache_service = cache_service

    async def execute(self, input_dto: AggregateBatchInputDTO) -> BatchEntity:
        """Закрывает партию с автоматическим сохранением доменных событий в outbox"""
        logger.info(f"Aggregating batch: batch_id={input_dto.batch_id}")
        try:
            async with self._uow:
                batch = await self._uow.batches.get_or_raise(input_dto.batch_id)
                batch.aggregate(input_dto.aggregated_at)
                if not batch.all_products_aggregated():
                    raise InvalidStateError("Не все продукты в партии агрегированы")
                for product in batch.products:
                    await self._uow.products.update(product)
                result = await self._uow.batches.update(batch)
                logger.info(f"Batch aggregated successfully: batch_id={input_dto.batch_id}")

            await self._invalidate_batch_cache(input_dto.batch_id)
            return result
        except Exception as e:
            logger.exception(f"Failed to aggregate batch: {e}")
            raise

    async def _invalidate_batch_cache(self, batch_id: UUID) -> None:
        """Инвалидирует кэш для партии (best effort)."""
        if not self._cache_service or not self._cache_service.enabled:
            return
        try:
            await self._cache_service.delete(get_batch_key(batch_id, self._cache_service.key_prefix))
            await self._cache_service.delete_pattern(get_batches_list_pattern(self._cache_service.key_prefix))
        except Exception as e:
            logger.warning(f"Failed to invalidate cache for batch {batch_id}: {e}")
