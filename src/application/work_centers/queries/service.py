from typing import Protocol
from uuid import UUID

from src.application.work_centers.queries.queries import ListWorkCentersQuery
from src.domain.common.queries import QueryResult
from src.domain.work_centers import WorkCenterEntity


class WorkCenterQueryServiceProtocol(Protocol):
    async def get(self, work_center_id: UUID) -> WorkCenterEntity | None:
        """Получает рабочий центр по UUID"""
        ...

    async def list(self, query: ListWorkCentersQuery) -> QueryResult[WorkCenterEntity]:
        """Получает список рабочих центров с фильтрацией, пагинацией и сортировкой"""
        ...
