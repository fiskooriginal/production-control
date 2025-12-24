from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from src.domain.batches.value_objects import BatchNumber
from src.domain.shared.events import DomainEvent


@dataclass(frozen=True)
class BatchCreatedEvent(DomainEvent):
    batch_number: BatchNumber
    batch_date: date
    work_center_id: UUID


@dataclass(frozen=True)
class BatchClosedEvent(DomainEvent):
    batch_number: BatchNumber
    closed_at: datetime


@dataclass(frozen=True)
class ProductAddedToBatchEvent(DomainEvent):
    product_id: UUID
    batch_id: UUID


@dataclass(frozen=True)
class ProductRemovedFromBatchEvent(DomainEvent):
    product_id: UUID
    batch_id: UUID
