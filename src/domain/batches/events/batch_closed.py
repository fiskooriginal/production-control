from dataclasses import dataclass
from datetime import datetime

from src.domain.batches.value_objects import BatchNumber
from src.domain.common.events import DomainEvent


@dataclass(frozen=True)
class BatchClosedEvent(DomainEvent):
    batch_number: BatchNumber
    closed_at: datetime
