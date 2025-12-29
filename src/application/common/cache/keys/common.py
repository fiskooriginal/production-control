from dataclasses import asdict


def serialize_filters(filters) -> dict:
    """Сериализует фильтры в словарь."""
    return asdict(filters)


def serialize_pagination(pagination) -> dict:
    """Сериализует пагинацию в словарь."""
    return asdict(pagination)


def serialize_sort(sort) -> dict:
    """Сериализует сортировку в словарь."""
    return asdict(sort)
