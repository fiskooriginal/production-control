from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from src.application.batches.queries.dtos.product_nested import ProductReadDTONested


@dataclass(frozen=True, slots=True, kw_only=True)
class BatchReadDTO:
    uuid: UUID
    created_at: datetime
    updated_at: datetime
    is_closed: bool
    closed_at: datetime | None
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
    products: list[ProductReadDTONested]
