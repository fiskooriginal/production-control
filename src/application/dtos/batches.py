from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateBatchInputDTO:
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


@dataclass(frozen=True, slots=True, kw_only=True)
class CloseBatchInputDTO:
    batch_id: UUID
    closed_at: datetime | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class BatchFilters:
    is_closed: bool | None = None
    batch_number: int | None = None
    batch_date: date | None = None
    work_center_id: UUID | None = None
    shift: str | None = None
