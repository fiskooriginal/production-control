from typing import ClassVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.queries.ports import WorkCenterQueryServiceProtocol
from src.application.queries.work_centers import (
    ListWorkCentersQuery,
    WorkCenterReadDTO,
    WorkCenterSortField,
)
from src.domain.common.queries import QueryResult
from src.infrastructure.exceptions import DatabaseException
from src.infrastructure.persistence.mappers.query import work_center_model_to_read_dto
from src.infrastructure.persistence.models.work_center import WorkCenter


class WorkCenterQueryService(WorkCenterQueryServiceProtocol):
    SORT_FIELD_MAPPING: ClassVar = {
        WorkCenterSortField.CREATED_AT: WorkCenter.created_at,
        WorkCenterSortField.UPDATED_AT: WorkCenter.updated_at,
        WorkCenterSortField.IDENTIFIER: WorkCenter.identifier,
        WorkCenterSortField.NAME: WorkCenter.name,
    }

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, work_center_id: UUID) -> WorkCenterReadDTO | None:
        """Получает рабочий центр по UUID"""
        try:
            work_center_model = await self._session.get(WorkCenter, work_center_id)
            if work_center_model is None:
                return None
            return work_center_model_to_read_dto(work_center_model)
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении рабочего центра: {e}") from e

    async def list(self, query: ListWorkCentersQuery) -> QueryResult[WorkCenterReadDTO]:
        """Получает список рабочих центров с фильтрацией, пагинацией и сортировкой"""
        try:
            stmt = select(WorkCenter)
            count_stmt = select(WorkCenter)

            if query.filters:
                stmt, count_stmt = self._apply_filters(stmt, count_stmt, query.filters)

            if query.sort:
                stmt = self._apply_sort(stmt, query.sort)

            total_result = await self._session.execute(select(func.count()).select_from(count_stmt.subquery()))
            total = total_result.scalar_one() or 0

            if query.pagination:
                stmt = stmt.offset(query.pagination.offset).limit(query.pagination.limit)

            result = await self._session.execute(stmt)
            work_centers = result.scalars().all()

            dtos = [work_center_model_to_read_dto(wc) for wc in work_centers]

            return QueryResult(
                items=dtos,
                total=total,
                limit=query.pagination.limit if query.pagination else None,
                offset=query.pagination.offset if query.pagination else None,
            )
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении списка рабочих центров: {e}") from e

    def _apply_filters(self, stmt, count_stmt, filters):
        """Применяет фильтры к запросу"""
        from src.application.queries.work_centers import WorkCenterReadFilters

        if not isinstance(filters, WorkCenterReadFilters):
            raise ValueError("filters должен быть типа WorkCenterReadFilters")

        if filters.identifier is not None:
            stmt = stmt.where(WorkCenter.identifier == filters.identifier)
            count_stmt = count_stmt.where(WorkCenter.identifier == filters.identifier)

        return stmt, count_stmt

    def _apply_sort(self, stmt, sort):
        """Применяет сортировку к запросу"""
        from src.application.queries.work_centers import WorkCenterSortSpec

        if not isinstance(sort, WorkCenterSortSpec):
            raise ValueError("sort должен быть типа WorkCenterSortSpec")

        column = self.SORT_FIELD_MAPPING.get(sort.field)
        if column is None:
            raise ValueError(f"Неизвестное поле сортировки: {sort.field}")

        if sort.direction.value == "desc":
            column = column.desc()

        return stmt.order_by(column)
