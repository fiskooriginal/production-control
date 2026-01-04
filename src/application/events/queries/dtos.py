from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class EventTypeReadDTO:
    uuid: UUID
    created_at: datetime
    updated_at: datetime
    name: str
    version: int
    webhook_enabled: bool
    description: str | None
