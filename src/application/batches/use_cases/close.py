from src.application.batches.dtos import CloseBatchInputDTO
from src.application.uow import UnitOfWorkProtocol
from src.core.logging import get_logger
from src.domain.batches.entities import BatchEntity
from src.domain.common.exceptions import InvalidStateError

logger = get_logger("use_case.batches")


class CloseBatchUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, input_dto: CloseBatchInputDTO) -> BatchEntity:
        """Закрывает партию с автоматическим сохранением доменных событий в outbox"""
        logger.info(f"Closing batch: batch_id={input_dto.batch_id}")
        try:
            async with self._uow:
                batch = await self._uow.batches.get_or_raise(input_dto.batch_id)
                if not batch.can_close():
                    raise InvalidStateError("Не все продукты в партии агрегированы")
                batch.close(input_dto.closed_at)
                result = await self._uow.batches.update(batch)
                logger.info(f"Batch closed successfully: batch_id={input_dto.batch_id}")
                return result
        except Exception as e:
            logger.exception(f"Failed to close batch: {e}")
            raise
