from typing import Protocol
from uuid import UUID

from src.application.work_centers.queries.dtos import WorkCenterReadDTO
from src.application.work_centers.queries.queries import ListWorkCentersQuery
from src.domain.common.queries import QueryResult


class WorkCenterQueryServiceProtocol(Protocol):
    async def get(self, work_center_id: UUID) -> WorkCenterReadDTO | None:
        """Получает рабочий центр по UUID"""
        ...

    async def list(self, query: ListWorkCentersQuery) -> QueryResult[WorkCenterReadDTO]:
        """Получает список рабочих центров с фильтрацией, пагинацией и сортировкой"""
        ...
