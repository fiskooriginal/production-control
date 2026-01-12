from src.application.batches.dtos.aggregate import AggregateBatchInputDTO
from src.application.common.uow.interfaces import UnitOfWorkProtocol
from src.core.logging import get_logger
from src.domain.batches import BatchEntity
from src.domain.common.exceptions import InvalidStateError

logger = get_logger("command.batches")


class AggregateBatchCommand:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

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
                return result
        except Exception as e:
            logger.exception(f"Failed to aggregate batch: {e}")
            raise
