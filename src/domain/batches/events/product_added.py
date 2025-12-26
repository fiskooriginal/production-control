from dataclasses import dataclass
from uuid import UUID

from src.domain.common.events import DomainEvent


@dataclass(frozen=True)
class ProductAddedToBatchEvent(DomainEvent):
    product_id: UUID
    batch_id: UUID
