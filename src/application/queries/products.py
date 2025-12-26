from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from src.domain.common.queries import PaginationSpec, SortDirection


class ProductSortField(str, Enum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    UNIQUE_CODE = "unique_code"
    IS_AGGREGATED = "is_aggregated"
    AGGREGATED_AT = "aggregated_at"


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductSortSpec:
    field: ProductSortField
    direction: SortDirection = SortDirection.ASC


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductReadDTO:
    uuid: UUID
    created_at: datetime
    updated_at: datetime
    unique_code: str
    batch_id: UUID
    is_aggregated: bool
    aggregated_at: datetime | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ListProductsQuery:
    pagination: PaginationSpec | None = None
    sort: ProductSortSpec | None = None
