from dataclasses import dataclass

from src.application.batches.queries.filters import BatchReadFilters
from src.application.batches.queries.sort import BatchSortSpec
from src.domain.common.queries import PaginationSpec


@dataclass(frozen=True, slots=True, kw_only=True)
class ListBatchesQuery:
    filters: BatchReadFilters | None = None
    pagination: PaginationSpec | None = None
    sort: BatchSortSpec | None = None
