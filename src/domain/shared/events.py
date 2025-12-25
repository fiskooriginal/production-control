from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.domain.shared.time import utc_now


@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime = field(default_factory=utc_now)
    aggregate_id: UUID
