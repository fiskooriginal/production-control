from uuid import UUID

from src.application.common.uow import UnitOfWorkProtocol
from src.core.logging import get_logger
from src.domain.batches.entities import BatchEntity
from src.domain.common.exceptions import InvalidStateError
from src.domain.products.entities import ProductEntity
from src.domain.products.value_objects import ProductCode

logger = get_logger("command.batches")


class AddProductToBatchCommand:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

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
                return batch
        except Exception as e:
            logger.exception(f"Failed to add product to batch: {e}")
            raise
