from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class BatchReadFilters:
    is_closed: bool | None = None
    batch_number: int | None = None
    batch_date: date | None = None
    work_center_id: UUID | None = None
    shift: str | None = None
