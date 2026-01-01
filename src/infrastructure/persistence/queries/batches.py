import json

from dataclasses import asdict
from typing import ClassVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.batches.queries import (
    BatchQueryServiceProtocol,
    ListBatchesQuery,
)
from src.application.batches.queries.sort import BatchSortField
from src.application.common.cache.interface.protocol import CacheServiceProtocol
from src.application.common.cache.keys import get_batch_key, get_batches_list_key
from src.core.logging import get_logger
from src.domain.batches import BatchEntity
from src.domain.common.queries import QueryResult
from src.infrastructure.common.exceptions import DatabaseException
from src.infrastructure.persistence.mappers.batches import (
    dict_to_domain,
    domain_to_json_bytes,
    json_bytes_to_domain,
    to_domain_entity,
)
from src.infrastructure.persistence.models.batch import Batch

logger = get_logger("query.batches")


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

    async def get(self, batch_id: UUID) -> BatchEntity | None:
        """Получает партию по UUID"""
        try:
            stmt = select(Batch).where(Batch.uuid == batch_id)
            result = await self._session.execute(stmt)
            batch_model = result.scalar_one_or_none()
            if batch_model is None:
                return None
            return to_domain_entity(batch_model)
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении партии: {e}") from e

    async def list(self, query: ListBatchesQuery) -> QueryResult[BatchEntity]:
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

            entities = [to_domain_entity(batch) for batch in batches]

            return QueryResult[BatchEntity](
                items=entities,
                total=total,
                limit=query.pagination.limit if query.pagination else None,
                offset=query.pagination.offset if query.pagination else None,
            )
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении списка партий: {e}") from e

    def _apply_filters(self, stmt, count_stmt, filters):
        """Применяет фильтры к запросу"""
        from src.application.batches.queries import BatchReadFilters

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
        from src.application.batches.queries.sort import BatchSortSpec

        if not isinstance(sort, BatchSortSpec):
            raise ValueError("sort должен быть типа BatchSortSpec")

        column = self.SORT_FIELD_MAPPING.get(sort.field)
        if column is None:
            raise ValueError(f"Неизвестное поле сортировки: {sort.field}")

        if sort.direction.value == "desc":
            column = column.desc()

        return stmt.order_by(column)


class CachedBatchQueryServiceProxy(BatchQueryService):
    """Обертка над BatchQueryService с добавлением кэширования."""

    def __init__(self, session: AsyncSession, cache_service: CacheServiceProtocol | None = None):
        super().__init__(session)
        self._cache_service = cache_service

    async def get(self, batch_id: UUID) -> BatchEntity | None:
        """Получает партию по UUID с кэшированием."""
        cache_key = get_batch_key(batch_id, self._cache_service.key_prefix)
        try:
            cached_data = await self._cache_service.get(cache_key)
            if cached_data:
                entity = json_bytes_to_domain(cached_data)
                if entity:
                    logger.info(f"Batch {batch_id} found in cache")
                    return entity
        except Exception as e:
            logger.warning(f"Failed to get batch from cache: {e}")

        logger.info("Fetching batch from database")
        entity = await super().get(batch_id)

        try:
            serialized = domain_to_json_bytes(entity)
            await self._cache_service.set(cache_key, serialized, ttl=self._cache_service.ttl_get)
        except Exception as e:
            logger.warning(f"Failed to cache batch: {e}")

        return entity

    async def list(self, query: ListBatchesQuery) -> QueryResult[BatchEntity]:
        """Получает список партий с фильтрацией, пагинацией и сортировкой с кэшированием."""
        cache_key = get_batches_list_key(query, self._cache_service.key_prefix)
        try:
            cached_data = await self._cache_service.get(cache_key)
            if cached_data:
                result = self._deserialize_query_result(cached_data)
                if result:
                    logger.info("Batches list found in cache")
                    return result
        except Exception as e:
            logger.warning(f"Failed to get batches list from cache: {e}")

        logger.info("Fetching batches list from database")
        query_result = await super().list(query)

        try:
            serialized = self._serialize_query_result(query_result)
            await self._cache_service.set(cache_key, serialized, ttl=self._cache_service.ttl_list)
        except Exception as e:
            logger.warning(f"Failed to cache batches list: {e}")

        return query_result

    @staticmethod
    def _serialize_query_result(result: QueryResult[BatchEntity]) -> bytes:
        """Сериализует QueryResult в JSON bytes."""
        result_dict = {
            "items": [asdict(item) for item in result.items],
            "total": result.total,
            "limit": result.limit,
            "offset": result.offset,
        }
        json_str = json.dumps(result_dict, default=str)
        return json_str.encode("utf-8")

    @staticmethod
    def _deserialize_query_result(data: bytes) -> QueryResult[BatchEntity] | None:
        """Десериализует JSON bytes в QueryResult[BatchEntity]."""
        try:
            json_str = data.decode("utf-8")
            result_dict = json.loads(json_str)
            items = [dict_to_domain(item) for item in result_dict.get("items", [])]
            return QueryResult[BatchEntity](
                items=items,
                total=result_dict.get("total", 0),
                limit=result_dict.get("limit"),
                offset=result_dict.get("offset"),
            )
        except Exception as e:
            logger.warning(f"Failed to deserialize QueryResult: {e}")
            return None
