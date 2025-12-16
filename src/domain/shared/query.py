from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class PaginationSpec:
    limit: int
    offset: int


@dataclass(frozen=True, slots=True, kw_only=True)
class SortSpec:
    field: str
    direction: str


@dataclass(frozen=True, slots=True, kw_only=True)
class QueryResult[T]:
    items: list[T]
    total: int
    limit: int | None
    offset: int | None
