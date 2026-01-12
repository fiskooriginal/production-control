from dataclasses import dataclass
from uuid import UUID

from src.domain.common.events import DomainEvent


@dataclass(frozen=True)
class WorkCenterDeletedEvent(DomainEvent):
    work_center_id: UUID
