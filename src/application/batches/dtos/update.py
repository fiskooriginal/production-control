from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateBatchInputDTO:
    batch_id: UUID
    task_description: str | None = None
    shift: str | None = None
    team: str | None = None
    batch_number: int | None = None
    batch_date: date | None = None
    nomenclature: str | None = None
    ekn_code: str | None = None
    shift_start: datetime | None = None
    shift_end: datetime | None = None
    work_center_id: UUID | None = None
    is_closed: bool | None = None
