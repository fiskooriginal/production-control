from uuid import UUID

from src.application.work_centers.queries.dtos import WorkCenterReadDTO
from src.application.work_centers.queries.service import WorkCenterQueryServiceProtocol
from src.core.logging import get_logger
from src.domain.common.exceptions import DoesNotExistError

logger = get_logger("query.handler.work_centers")


class GetWorkCenterQueryHandler:
    def __init__(self, query_service: WorkCenterQueryServiceProtocol):
        self._query_service = query_service

    async def execute(self, work_center_id: UUID) -> WorkCenterReadDTO:
        """Получает рабочий центр по UUID"""
        logger.debug(f"Getting work center: work_center_id={work_center_id}")
        try:
            result = await self._query_service.get(work_center_id)
            if result is None:
                raise DoesNotExistError(f"Рабочий центр с UUID {work_center_id} не найден")
            logger.debug(f"Work center retrieved: work_center_id={work_center_id}")
            return result
        except DoesNotExistError:
            raise
        except Exception as e:
            logger.exception(f"Failed to get work center: {e}")
            raise
