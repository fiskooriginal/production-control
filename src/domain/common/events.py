from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.core.time import datetime_now


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    aggregate_id: UUID
    occurred_at: datetime = field(default_factory=datetime_now)
