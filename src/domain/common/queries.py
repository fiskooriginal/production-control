from dataclasses import dataclass
from enum import Enum


class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


@dataclass(frozen=True, slots=True, kw_only=True)
class PaginationSpec:
    limit: int
    offset: int


@dataclass(frozen=True, slots=True, kw_only=True)
class SortSpec:
    field: str
    direction: SortDirection = SortDirection.ASC


@dataclass(frozen=True, slots=True, kw_only=True)
class QueryResult[T]:
    items: list[T]
    total: int
    limit: int | None
    offset: int | None
