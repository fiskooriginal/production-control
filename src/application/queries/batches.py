from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from uuid import UUID

from src.domain.shared.queries import PaginationSpec, SortDirection


class BatchSortField(str, Enum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    BATCH_NUMBER = "batch_number"
    BATCH_DATE = "batch_date"
    SHIFT = "shift"
    TEAM = "team"
    IS_CLOSED = "is_closed"


@dataclass(frozen=True, slots=True, kw_only=True)
class BatchSortSpec:
    field: BatchSortField
    direction: SortDirection = SortDirection.ASC


@dataclass(frozen=True, slots=True, kw_only=True)
class BatchReadFilters:
    is_closed: bool | None = None
    batch_number: int | None = None
    batch_date: date | None = None
    work_center_id: UUID | None = None
    shift: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductReadDTONested:
    uuid: UUID
    created_at: datetime
    updated_at: datetime
    unique_code: str
    batch_id: UUID
    is_aggregated: bool
    aggregated_at: datetime | None


@dataclass(frozen=True, slots=True, kw_only=True)
class BatchReadDTO:
    uuid: UUID
    created_at: datetime
    updated_at: datetime
    is_closed: bool
    closed_at: datetime | None
    task_description: str
    shift: str
    team: str
    batch_number: int
    batch_date: date
    nomenclature: str
    ekn_code: str
    shift_start: datetime
    shift_end: datetime
    work_center_id: UUID
    products: list[ProductReadDTONested]


@dataclass(frozen=True, slots=True, kw_only=True)
class ListBatchesQuery:
    filters: BatchReadFilters | None = None
    pagination: PaginationSpec | None = None
    sort: BatchSortSpec | None = None
