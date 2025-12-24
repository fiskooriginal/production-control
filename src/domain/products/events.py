from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.shared.events import DomainEvent


@dataclass(frozen=True)
class ProductAggregatedEvent(DomainEvent):
    product_id: UUID
    batch_id: UUID
    aggregated_at: datetime
