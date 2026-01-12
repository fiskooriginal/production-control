from typing import ClassVar

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.work_centers.queries.filters import WorkCenterReadFilters
from src.application.work_centers.queries.queries import ListWorkCentersQuery
from src.application.work_centers.queries.service import WorkCenterQueryServiceProtocol
from src.application.work_centers.queries.sort import WorkCenterSortField
from src.domain.work_centers import WorkCenterEntity
from src.infrastructure.persistence.mappers.work_centers import to_domain_entity
from src.infrastructure.persistence.models.work_center import WorkCenter
from src.infrastructure.persistence.queries.base import BaseQueryService


class WorkCenterQueryService(
    BaseQueryService[WorkCenterEntity, WorkCenter, ListWorkCentersQuery, WorkCenterReadFilters, WorkCenterSortField],
    WorkCenterQueryServiceProtocol,
):
    SORT_FIELD_MAPPING: ClassVar = {
        WorkCenterSortField.CREATED_AT: WorkCenter.created_at,
        WorkCenterSortField.UPDATED_AT: WorkCenter.updated_at,
        WorkCenterSortField.IDENTIFIER: WorkCenter.identifier,
        WorkCenterSortField.NAME: WorkCenter.name,
    }

    def __init__(self, session: AsyncSession):
        super().__init__(session, WorkCenter, to_domain_entity)

    def _apply_filters(
        self,
        stmt: Select,
        count_stmt: Select,
        filters: WorkCenterReadFilters | None,
    ) -> tuple[Select, Select]:
        """Применяет фильтры к запросу"""
        if filters is None:
            return stmt, count_stmt

        if filters.identifier is not None:
            stmt = stmt.where(WorkCenter.identifier == filters.identifier)
            count_stmt = count_stmt.where(WorkCenter.identifier == filters.identifier)

        return stmt, count_stmt
