from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class AggregateBatchInputDTO:
    batch_id: UUID
    aggregated_at: datetime | None = None
