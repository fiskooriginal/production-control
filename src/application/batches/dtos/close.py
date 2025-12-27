from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class CloseBatchInputDTO:
    batch_id: UUID
    closed_at: datetime | None = None
