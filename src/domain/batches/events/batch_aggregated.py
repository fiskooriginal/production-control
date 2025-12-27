from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.common.events import DomainEvent


@dataclass(frozen=True)
class BatchAggregatedEvent(DomainEvent):
    batch_id: UUID
    aggregated_at: datetime
