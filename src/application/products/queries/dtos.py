from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductReadDTO:
    uuid: UUID
    created_at: datetime
    updated_at: datetime
    unique_code: str
    batch_id: UUID
    is_aggregated: bool
    aggregated_at: datetime | None
