from uuid import UUID

from src.application.common.uow.interfaces import UnitOfWorkProtocol
from src.core.logging import get_logger
from src.domain.work_centers.events import WorkCenterDeletedEvent

logger = get_logger("command.work_centers")


class DeleteWorkCenterCommand:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, work_center_id: UUID) -> None:
        """Удаляет рабочий центр"""
        logger.info(f"Deleting work center: work_center_id={work_center_id}")
        try:
            async with self._uow:
                work_center = await self._uow.work_centers.get_or_raise(work_center_id)
                await self._uow.work_centers.delete(work_center_id)
                work_center.add_domain_event(
                    WorkCenterDeletedEvent(work_center_id=work_center_id, aggregate_id=work_center_id)
                )
                logger.info(f"Work center deleted successfully: work_center_id={work_center_id}")
        except Exception as e:
            logger.exception(f"Failed to delete work center: {e}")
            raise
