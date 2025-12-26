from uuid import UUID

from src.application.queries.ports import WorkCenterQueryServiceProtocol
from src.application.queries.work_centers import ListWorkCentersQuery, WorkCenterReadDTO
from src.core.logging import get_logger
from src.domain.shared.exceptions import DoesNotExistError
from src.domain.shared.queries import QueryResult

logger = get_logger("use_case.queries.work_centers")


class GetWorkCenterQueryUseCase:
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


class ListWorkCentersQueryUseCase:
    def __init__(self, query_service: WorkCenterQueryServiceProtocol):
        self._query_service = query_service

    async def execute(self, query: ListWorkCentersQuery) -> QueryResult[WorkCenterReadDTO]:
        """Получает список рабочих центров с фильтрацией, пагинацией и сортировкой"""
        logger.debug(f"Listing work centers: filters={query.filters}")
        try:
            result = await self._query_service.list(query)
            logger.debug(f"Listed {result.total} work centers")
            return result
        except Exception as e:
            logger.exception(f"Failed to list work centers: {e}")
            raise
