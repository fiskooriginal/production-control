from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from src.domain.common.queries import PaginationSpec, SortDirection


class WorkCenterSortField(str, Enum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    IDENTIFIER = "identifier"
    NAME = "name"


@dataclass(frozen=True, slots=True, kw_only=True)
class WorkCenterSortSpec:
    field: WorkCenterSortField
    direction: SortDirection = SortDirection.ASC


@dataclass(frozen=True, slots=True, kw_only=True)
class WorkCenterReadFilters:
    identifier: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class WorkCenterReadDTO:
    uuid: UUID
    created_at: datetime
    updated_at: datetime
    identifier: str
    name: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ListWorkCentersQuery:
    filters: WorkCenterReadFilters | None = None
    pagination: PaginationSpec | None = None
    sort: WorkCenterSortSpec | None = None
