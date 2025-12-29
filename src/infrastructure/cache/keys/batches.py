import hashlib
import json

from uuid import UUID

from src.application.batches.queries import ListBatchesQuery
from src.infrastructure.cache.keys.common import serialize_filters, serialize_pagination, serialize_sort


def get_batch_key(batch_id: UUID, prefix: str = "cache") -> str:
    """Генерирует ключ кэша для отдельной партии."""
    return f"{prefix}:batch:{batch_id}"


def get_batches_list_key(query: ListBatchesQuery, prefix: str = "cache") -> str:
    """Генерирует ключ кэша для списка партий на основе фильтров, пагинации и сортировки."""
    query_dict = {
        "filters": serialize_filters(query.filters) if query.filters else None,
        "pagination": serialize_pagination(query.pagination) if query.pagination else None,
        "sort": serialize_sort(query.sort) if query.sort else None,
    }
    query_json = json.dumps(query_dict, sort_keys=True, default=str)
    query_hash = hashlib.sha256(query_json.encode()).hexdigest()[:16]
    return f"{prefix}:batches:list:{query_hash}"


def get_batches_list_pattern(prefix: str = "cache") -> str:
    """Возвращает паттерн для всех ключей списков партий."""
    return f"{prefix}:batches:list:*"
