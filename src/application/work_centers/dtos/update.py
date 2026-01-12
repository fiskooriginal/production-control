from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateWorkCenterInputDTO:
    work_center_id: UUID
    identifier: str | None = None
    name: str | None = None
