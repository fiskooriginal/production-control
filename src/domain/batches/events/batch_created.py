from dataclasses import dataclass
from datetime import date
from uuid import UUID

from src.domain.batches.value_objects import BatchNumber
from src.domain.common.events import DomainEvent


@dataclass(frozen=True)
class BatchCreatedEvent(DomainEvent):
    batch_number: BatchNumber
    batch_date: date
    work_center_id: UUID
