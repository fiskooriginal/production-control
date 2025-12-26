from typing import ClassVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.queries.batches import BatchReadDTO, BatchSortField, ListBatchesQuery
from src.application.queries.ports import BatchQueryServiceProtocol
from src.domain.common.queries import QueryResult
from src.infrastructure.exceptions import DatabaseException
from src.infrastructure.persistence.mappers.query import batch_model_to_read_dto
from src.infrastructure.persistence.models.batch import Batch


class BatchQueryService(BatchQueryServiceProtocol):
    SORT_FIELD_MAPPING: ClassVar = {
        BatchSortField.CREATED_AT: Batch.created_at,
        BatchSortField.UPDATED_AT: Batch.updated_at,
        BatchSortField.BATCH_NUMBER: Batch.batch_number,
        BatchSortField.BATCH_DATE: Batch.batch_date,
        BatchSortField.SHIFT: Batch.shift,
        BatchSortField.TEAM: Batch.team,
        BatchSortField.IS_CLOSED: Batch.is_closed,
    }

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, batch_id: UUID) -> BatchReadDTO | None:
        """Получает партию по UUID"""
        try:
            stmt = select(Batch).where(Batch.uuid == batch_id)
            result = await self._session.execute(stmt)
            batch_model = result.scalar_one_or_none()
            if batch_model is None:
                return None
            return batch_model_to_read_dto(batch_model)
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении партии: {e}") from e

    async def list(self, query: ListBatchesQuery) -> QueryResult[BatchReadDTO]:
        """Получает список партий с фильтрацией, пагинацией и сортировкой"""
        try:
            stmt = select(Batch)
            count_stmt = select(Batch)

            if query.filters:
                stmt, count_stmt = self._apply_filters(stmt, count_stmt, query.filters)

            if query.sort:
                stmt = self._apply_sort(stmt, query.sort)

            total_result = await self._session.execute(select(func.count()).select_from(count_stmt.subquery()))
            total = total_result.scalar_one() or 0

            if query.pagination:
                stmt = stmt.offset(query.pagination.offset).limit(query.pagination.limit)

            result = await self._session.execute(stmt)
            batches = result.scalars().all()

            dtos = [batch_model_to_read_dto(batch) for batch in batches]

            return QueryResult(
                items=dtos,
                total=total,
                limit=query.pagination.limit if query.pagination else None,
                offset=query.pagination.offset if query.pagination else None,
            )
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении списка партий: {e}") from e

    def _apply_filters(self, stmt, count_stmt, filters):
        """Применяет фильтры к запросу"""
        from src.application.queries.batches import BatchReadFilters

        if not isinstance(filters, BatchReadFilters):
            raise ValueError("filters должен быть типа BatchReadFilters")

        if filters.is_closed is not None:
            stmt = stmt.where(Batch.is_closed == filters.is_closed)
            count_stmt = count_stmt.where(Batch.is_closed == filters.is_closed)

        if filters.batch_number is not None:
            stmt = stmt.where(Batch.batch_number == filters.batch_number)
            count_stmt = count_stmt.where(Batch.batch_number == filters.batch_number)

        if filters.batch_date is not None:
            stmt = stmt.where(Batch.batch_date == filters.batch_date)
            count_stmt = count_stmt.where(Batch.batch_date == filters.batch_date)

        if filters.work_center_id is not None:
            stmt = stmt.where(Batch.work_center_id == filters.work_center_id)
            count_stmt = count_stmt.where(Batch.work_center_id == filters.work_center_id)

        if filters.shift is not None:
            stmt = stmt.where(Batch.shift == filters.shift)
            count_stmt = count_stmt.where(Batch.shift == filters.shift)

        return stmt, count_stmt

    def _apply_sort(self, stmt, sort):
        """Применяет сортировку к запросу"""
        from src.application.queries.batches import BatchSortSpec

        if not isinstance(sort, BatchSortSpec):
            raise ValueError("sort должен быть типа BatchSortSpec")

        column = self.SORT_FIELD_MAPPING.get(sort.field)
        if column is None:
            raise ValueError(f"Неизвестное поле сортировки: {sort.field}")

        if sort.direction.value == "desc":
            column = column.desc()

        return stmt.order_by(column)
