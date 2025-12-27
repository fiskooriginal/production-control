from dataclasses import dataclass

from src.application.batches.queries.sort.field import BatchSortField
from src.domain.common.queries import SortDirection


@dataclass(frozen=True, slots=True, kw_only=True)
class BatchSortSpec:
    field: BatchSortField
    direction: SortDirection = SortDirection.ASC
