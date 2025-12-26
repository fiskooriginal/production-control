from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.domain.common.time import utc_now


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    aggregate_id: UUID
    occurred_at: datetime = field(default_factory=utc_now)
