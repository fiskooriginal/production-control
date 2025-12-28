import hashlib
import json

from uuid import UUID

from src.application.batches.queries import ListBatchesQuery


def get_batch_key(batch_id: UUID, prefix: str = "cache") -> str:
    """Генерирует ключ кэша для отдельной партии."""
    return f"{prefix}:batch:{batch_id}"


def get_batches_list_key(query: ListBatchesQuery, prefix: str = "cache") -> str:
    """Генерирует ключ кэша для списка партий на основе фильтров, пагинации и сортировки."""
    query_dict = {
        "filters": _serialize_filters(query.filters) if query.filters else None,
        "pagination": _serialize_pagination(query.pagination) if query.pagination else None,
        "sort": _serialize_sort(query.sort) if query.sort else None,
    }
    query_json = json.dumps(query_dict, sort_keys=True, default=str)
    query_hash = hashlib.sha256(query_json.encode()).hexdigest()[:16]
    return f"{prefix}:batches:list:{query_hash}"


def get_batches_list_pattern(prefix: str = "cache") -> str:
    """Возвращает паттерн для всех ключей списков партий."""
    return f"{prefix}:batches:list:*"


def _serialize_filters(filters) -> dict:
    """Сериализует фильтры в словарь."""
    from dataclasses import asdict

    return asdict(filters)


def _serialize_pagination(pagination) -> dict:
    """Сериализует пагинацию в словарь."""
    from dataclasses import asdict

    return asdict(pagination)


def _serialize_sort(sort) -> dict:
    """Сериализует сортировку в словарь."""
    from dataclasses import asdict

    return asdict(sort)
