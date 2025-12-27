from dataclasses import dataclass

from src.application.work_centers.queries.sort.field import WorkCenterSortField
from src.domain.common.queries import SortDirection


@dataclass(frozen=True, slots=True, kw_only=True)
class WorkCenterSortSpec:
    field: WorkCenterSortField
    direction: SortDirection = SortDirection.ASC
