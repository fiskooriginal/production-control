from dataclasses import dataclass

from src.domain.batches.value_objects import BatchNumber
from src.domain.common.events import DomainEvent


@dataclass(frozen=True)
class BatchDeletedEvent(DomainEvent):
    batch_number: BatchNumber
