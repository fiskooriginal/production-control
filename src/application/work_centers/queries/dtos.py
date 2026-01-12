from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class WorkCenterReadDTO:
    uuid: UUID
    created_at: datetime
    updated_at: datetime
    identifier: str
    name: str
