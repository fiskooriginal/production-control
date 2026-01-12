from dataclasses import dataclass
from uuid import UUID

from src.domain.common.events import DomainEvent


@dataclass(frozen=True)
class BatchesImportCompletedEvent(DomainEvent):
    task_id: UUID
    update_existing: bool
    total_rows: int
    created: int
    updated: int
    skipped: int
    errors: list
