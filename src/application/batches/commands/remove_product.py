from uuid import UUID

from src.application.common.uow.interfaces import UnitOfWorkProtocol
from src.core.logging import get_logger
from src.domain.batches import BatchEntity
from src.domain.common.exceptions import InvalidStateError

logger = get_logger("command.batches")


class RemoveProductFromBatchCommand:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

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
                return batch
        except Exception as e:
            logger.exception(f"Failed to remove product from batch: {e}")
            raise
