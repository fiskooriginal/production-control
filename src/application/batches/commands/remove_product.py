from uuid import UUID

from src.application.common.uow import UnitOfWorkProtocol
from src.core.logging import get_logger
from src.domain.batches.entities import BatchEntity
from src.domain.common.exceptions import InvalidStateError
from src.infrastructure.cache.keys import get_batch_key, get_batches_list_pattern
from src.infrastructure.cache.protocol import CacheServiceProtocol

logger = get_logger("command.batches")


class RemoveProductFromBatchCommand:
    def __init__(self, uow: UnitOfWorkProtocol, cache_service: CacheServiceProtocol | None = None):
        self._uow = uow
        self._cache_service = cache_service

    async def execute(self, batch_id: UUID, product_id: UUID) -> BatchEntity:
        """Удаляет продукт из партии с автоматическим сохранением доменных событий в outbox"""
        logger.info(f"Removing product from batch: batch_id={batch_id} product_id={product_id}")
        try:
            async with self._uow:
                batch = await self._uow.batches.get_or_raise(batch_id)

                if batch.is_closed:
                    raise InvalidStateError("Нельзя удалять продукты из закрытой партии")

                product = await self._uow.products.get_or_raise(product_id)

                if product.batch_id != batch_id:
                    raise InvalidStateError("Продукт не принадлежит этой партии")

                await self._uow.products.delete(product_id)
                batch.remove_product(product)
                await self._uow.batches.update(batch)
                logger.info(f"Product removed from batch successfully: product_id={product_id}")

            await self._invalidate_batch_cache(batch_id)
            return batch
        except Exception as e:
            logger.exception(f"Failed to remove product from batch: {e}")
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
