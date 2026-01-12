import json

from dataclasses import asdict
from typing import ClassVar
from uuid import UUID

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.batches.queries.filters import BatchReadFilters
from src.application.batches.queries.queries import ListBatchesQuery
from src.application.batches.queries.service import BatchQueryServiceProtocol
from src.application.batches.queries.sort import BatchSortField
from src.application.common.cache.interfaces import CacheServiceProtocol
from src.application.common.cache.keys.batches import get_batch_key, get_batches_list_key
from src.core.logging import get_logger
from src.core.settings import BatchCacheSettings
from src.domain.batches import BatchEntity
from src.domain.common.queries import QueryResult
from src.infrastructure.persistence.mappers.batches import (
    dict_to_domain,
    domain_to_json_bytes,
    json_bytes_to_domain,
    to_domain_entity,
)
from src.infrastructure.persistence.models.batch import Batch
from src.infrastructure.persistence.queries.base import BaseQueryService

logger = get_logger("query.batches")


class BatchQueryService(
    BaseQueryService[BatchEntity, Batch, ListBatchesQuery, BatchReadFilters, BatchSortField],
    BatchQueryServiceProtocol,
):
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
        super().__init__(session, Batch, to_domain_entity)

    def _apply_filters(
        self,
        stmt: Select,
        count_stmt: Select,
        filters: BatchReadFilters | None,
    ) -> tuple[Select, Select]:
        """Применяет фильтры к запросу"""
        if filters is None:
            return stmt, count_stmt

        if filters.is_closed is not None:
            stmt = stmt.where(Batch.is_closed == filters.is_closed)
            count_stmt = count_stmt.where(Batch.is_closed == filters.is_closed)

        if filters.batch_number is not None:
            stmt = stmt.where(Batch.batch_number == filters.batch_number)
            count_stmt = count_stmt.where(Batch.batch_number == filters.batch_number)

        if filters.batch_date is not None:
            stmt = stmt.where(Batch.batch_date == filters.batch_date)
            count_stmt = count_stmt.where(Batch.batch_date == filters.batch_date)

        if filters.batch_date_from is not None:
            stmt = stmt.where(Batch.batch_date >= filters.batch_date_from)
            count_stmt = count_stmt.where(Batch.batch_date >= filters.batch_date_from)

        if filters.batch_date_to is not None:
            stmt = stmt.where(Batch.batch_date <= filters.batch_date_to)
            count_stmt = count_stmt.where(Batch.batch_date <= filters.batch_date_to)

        if filters.work_center_id is not None:
            stmt = stmt.where(Batch.work_center_id == filters.work_center_id)
            count_stmt = count_stmt.where(Batch.work_center_id == filters.work_center_id)

        if filters.shift is not None:
            stmt = stmt.where(Batch.shift == filters.shift)
            count_stmt = count_stmt.where(Batch.shift == filters.shift)

        return stmt, count_stmt


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
            batch_cache_settings = BatchCacheSettings()
            await self._cache_service.set(cache_key, serialized, ttl=batch_cache_settings.ttl_get)
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
            batch_cache_settings = BatchCacheSettings()
            await self._cache_service.set(cache_key, serialized, ttl=batch_cache_settings.ttl_list)
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
