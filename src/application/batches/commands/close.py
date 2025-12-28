from uuid import UUID

from src.application.batches.dtos import CloseBatchInputDTO
from src.application.common.uow import UnitOfWorkProtocol
from src.core.logging import get_logger
from src.domain.batches.entities import BatchEntity
from src.infrastructure.cache.keys import get_batch_key, get_batches_list_pattern
from src.infrastructure.cache.protocol import CacheServiceProtocol

logger = get_logger("command.batches")


class CloseBatchCommand:
    def __init__(self, uow: UnitOfWorkProtocol, cache_service: CacheServiceProtocol | None = None):
        self._uow = uow
        self._cache_service = cache_service

    async def execute(self, input_dto: CloseBatchInputDTO) -> BatchEntity:
        """Закрывает партию с автоматическим сохранением доменных событий в outbox"""
        logger.info(f"Closing batch: batch_id={input_dto.batch_id}")
        try:
            async with self._uow:
                batch = await self._uow.batches.get_or_raise(input_dto.batch_id)
                batch.close(input_dto.closed_at)
                result = await self._uow.batches.update(batch)
                logger.info(f"Batch closed successfully: batch_id={input_dto.batch_id}")

            await self._invalidate_batch_cache(input_dto.batch_id)
            return result
        except Exception as e:
            logger.exception(f"Failed to close batch: {e}")
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
