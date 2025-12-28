import json

from dataclasses import asdict, fields
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.batches.queries import BatchReadDTO, ListBatchesQuery
from src.application.batches.queries.dtos import ProductReadDTONested
from src.core.logging import get_logger
from src.domain.common.queries import QueryResult
from src.infrastructure.cache.keys import get_batch_key, get_batches_list_key
from src.infrastructure.cache.protocol import CacheServiceProtocol
from src.infrastructure.persistence.queries.batches import BatchQueryService

logger = get_logger("query.batches.cached")


class CachedBatchQueryService(BatchQueryService):
    """Обертка над BatchQueryService с добавлением кэширования."""

    def __init__(self, session: AsyncSession, cache_service: CacheServiceProtocol | None = None):
        super().__init__(session)
        self._cache_service = cache_service

    async def get(self, batch_id: UUID) -> BatchReadDTO | None:
        """Получает партию по UUID с кэшированием."""
        cache_key = get_batch_key(batch_id, self._cache_service.key_prefix)
        try:
            cached_data = await self._cache_service.get(cache_key)
            if cached_data:
                dto = self._deserialize_batch_dto(cached_data)
                if dto:
                    logger.info(f"Batch {batch_id} found in cache")
                    return dto
        except Exception as e:
            logger.warning(f"Failed to get batch from cache: {e}")

        logger.info("Fetching batch from database")
        dto = await super().get(batch_id)

        try:
            serialized = self._serialize_batch_dto(dto)
            await self._cache_service.set(cache_key, serialized, ttl=self._cache_service.ttl_batch)
        except Exception as e:
            logger.warning(f"Failed to cache batch: {e}")

        return dto

    async def list(self, query: ListBatchesQuery) -> QueryResult[BatchReadDTO]:
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

    def _serialize_batch_dto(self, dto: BatchReadDTO) -> bytes:
        """Сериализует BatchReadDTO в JSON bytes."""
        dto_dict = asdict(dto)
        json_str = json.dumps(dto_dict, default=str)
        return json_str.encode("utf-8")

    def _deserialize_batch_dto(self, data: bytes) -> BatchReadDTO | None:
        """Десериализует JSON bytes в BatchReadDTO."""
        try:
            json_str = data.decode("utf-8")
            dto_dict = json.loads(json_str)
            field_names = {f.name for f in fields(BatchReadDTO)}
            filtered_dict = {k: v for k, v in dto_dict.items() if k in field_names}
            products = [ProductReadDTONested(**p) for p in filtered_dict.pop("products", [])]
            return BatchReadDTO(**filtered_dict, products=products)
        except Exception as e:
            logger.warning(f"Failed to deserialize BatchReadDTO: {e}")
            return None

    def _serialize_query_result(self, result: QueryResult[BatchReadDTO]) -> bytes:
        """Сериализует QueryResult в JSON bytes."""
        result_dict = {
            "items": [asdict(item) for item in result.items],
            "total": result.total,
            "limit": result.limit,
            "offset": result.offset,
        }
        json_str = json.dumps(result_dict, default=str)
        return json_str.encode("utf-8")

    def _deserialize_query_result(self, data: bytes) -> QueryResult[BatchReadDTO] | None:
        """Десериализует JSON bytes в QueryResult[BatchReadDTO]."""
        try:
            json_str = data.decode("utf-8")
            result_dict = json.loads(json_str)
            items = [self._deserialize_batch_dto_item(item) for item in result_dict.get("items", [])]
            return QueryResult(
                items=items,
                total=result_dict.get("total", 0),
                limit=result_dict.get("limit"),
                offset=result_dict.get("offset"),
            )
        except Exception as e:
            logger.warning(f"Failed to deserialize QueryResult: {e}")
            return None

    def _deserialize_batch_dto_item(self, item_dict: dict) -> BatchReadDTO:
        """Десериализует отдельный элемент BatchReadDTO из словаря."""
        from src.application.batches.queries.dtos.product_nested import ProductReadDTONested

        field_names = {f.name for f in fields(BatchReadDTO)}
        filtered_dict = {k: v for k, v in item_dict.items() if k in field_names}

        if "products" in filtered_dict and isinstance(filtered_dict["products"], list):
            product_field_names = {f.name for f in fields(ProductReadDTONested)}
            filtered_dict["products"] = [
                ProductReadDTONested(**{k: v for k, v in p.items() if k in product_field_names})
                for p in filtered_dict["products"]
            ]

        return BatchReadDTO(**filtered_dict)
