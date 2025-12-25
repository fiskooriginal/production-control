from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateWorkCenterInputDTO:
    identifier: str
    name: str


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateWorkCenterInputDTO:
    work_center_id: UUID
    identifier: str | None = None
    name: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class WorkCenterFilters:
    identifier: str | None = None
