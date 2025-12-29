from uuid import UUID

from src.application.common.uow import UnitOfWorkProtocol
from src.core.logging import get_logger
from src.domain.batches.entities import BatchEntity
from src.domain.common.exceptions import InvalidStateError
from src.domain.products.entities import ProductEntity
from src.domain.products.value_objects import ProductCode
from src.infrastructure.cache.keys.batches import get_batch_key, get_batches_list_pattern
from src.infrastructure.cache.protocol import CacheServiceProtocol

logger = get_logger("command.batches")


class AddProductToBatchCommand:
    def __init__(self, uow: UnitOfWorkProtocol, cache_service: CacheServiceProtocol | None = None):
        self._uow = uow
        self._cache_service = cache_service

    async def execute(self, batch_id: UUID, unique_code: str) -> BatchEntity:
        """Добавляет продукт в партию с автоматическим сохранением доменных событий в outbox"""
        logger.info(f"Adding product to batch: batch_id={batch_id} unique_code={unique_code}")
        try:
            async with self._uow:
                batch = await self._uow.batches.get_or_raise(batch_id)

                if batch.is_closed:
                    raise InvalidStateError("Нельзя добавлять продукты в закрытую партию")

                product = ProductEntity(unique_code=ProductCode(unique_code), batch_id=batch_id)

                await self._uow.products.create(product)
                batch.add_product(product)
                await self._uow.batches.update(batch)
                logger.info(f"Product added to batch successfully: product_id={product.uuid}")

            await self._invalidate_batch_cache(batch_id)
            return batch
        except Exception as e:
            logger.exception(f"Failed to add product to batch: {e}")
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
