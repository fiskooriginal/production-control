from src.application.work_centers.queries.dtos import WorkCenterReadDTO
from src.application.work_centers.queries.queries import ListWorkCentersQuery
from src.application.work_centers.queries.service import WorkCenterQueryServiceProtocol
from src.core.logging import get_logger
from src.domain.common.queries import QueryResult

logger = get_logger("use_case.queries.work_centers")


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
