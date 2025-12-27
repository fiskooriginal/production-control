from dataclasses import dataclass
from datetime import datetime

from src.domain.batches.value_objects import BatchNumber
from src.domain.common.events import DomainEvent


@dataclass(frozen=True)
class BatchOpenedEvent(DomainEvent):
    batch_number: BatchNumber
    opened_at: datetime
