from dataclasses import dataclass

from src.application.work_centers.queries.filters import WorkCenterReadFilters
from src.application.work_centers.queries.sort import WorkCenterSortSpec
from src.domain.common.queries import PaginationSpec


@dataclass(frozen=True, slots=True, kw_only=True)
class ListWorkCentersQuery:
    filters: WorkCenterReadFilters | None = None
    pagination: PaginationSpec | None = None
    sort: WorkCenterSortSpec | None = None
