from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.common.entities import BaseEntity
from src.domain.common.exceptions import InvalidStateError
from src.domain.common.time import utc_now
from src.domain.products.events import ProductAggregatedEvent
from src.domain.products.value_objects import ProductCode


@dataclass(slots=True, kw_only=True)
class ProductEntity(BaseEntity):
    unique_code: ProductCode
    batch_id: UUID
    is_aggregated: bool = False
    aggregated_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.is_aggregated and self.aggregated_at is None:
            raise InvalidStateError("Время агрегации должно быть установлено для агрегированного продукта")
        if not self.is_aggregated and self.aggregated_at is not None:
            raise InvalidStateError("Время агрегации должно быть пустым для неагрегированного продукта")

    def aggregate(self, aggregated_at: datetime | None = None) -> None:
        """Агрегирует продукт"""
        if self.is_aggregated:
            raise InvalidStateError("Продукт уже агрегирован")
        if aggregated_at is None:
            aggregated_at = utc_now()
        self.is_aggregated = True
        self.aggregated_at = aggregated_at
        self.updated_at = utc_now()
        self.add_domain_event(
            ProductAggregatedEvent(
                aggregate_id=self.uuid, product_id=self.uuid, batch_id=self.batch_id, aggregated_at=aggregated_at
            )
        )
