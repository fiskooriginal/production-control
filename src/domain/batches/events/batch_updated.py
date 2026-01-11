from dataclasses import dataclass
from datetime import datetime

from src.domain.batches.value_objects import BatchNumber
from src.domain.common.events import DomainEvent


@dataclass(frozen=True)
class BatchUpdatedEvent(DomainEvent):
    batch_number: BatchNumber
    updated_at: datetime
