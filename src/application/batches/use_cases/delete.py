from uuid import UUID

from src.application.common.uow import UnitOfWorkProtocol
from src.core.logging import get_logger
from src.domain.batches.events import BatchDeletedEvent
from src.domain.common.exceptions import InvalidStateError

logger = get_logger("use_case.batches")


class DeleteBatchUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, batch_id: UUID) -> None:
        """Удаляет закрытую партию с автоматическим сохранением доменных событий в outbox"""
        logger.info(f"Deleting batch: batch_id={batch_id}")
        try:
            async with self._uow:
                batch = await self._uow.batches.get_or_raise(batch_id)

                if not batch.is_closed:
                    raise InvalidStateError("Можно удалить только закрытую партию")

                batch.add_domain_event(BatchDeletedEvent(aggregate_id=batch.uuid, batch_number=batch.batch_number))
                await self._uow.batches.delete(batch_id)
                logger.info(f"Batch deleted successfully: batch_id={batch_id}")
        except Exception as e:
            logger.exception(f"Failed to delete batch: {e}")
            raise
