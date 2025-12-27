from dataclasses import dataclass
from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from src.core.time import datetime_now
from src.domain.batches.events import BatchClosedEvent, ProductAddedToBatchEvent, ProductRemovedFromBatchEvent
from src.domain.batches.value_objects import (
    BatchNumber,
    EknCode,
    Nomenclature,
    Shift,
    ShiftTimeRange,
    TaskDescription,
    Team,
)
from src.domain.common.entities import BaseEntity
from src.domain.common.exceptions import InvalidStateError

if TYPE_CHECKING:
    from src.domain.products.entities import ProductEntity


@dataclass(slots=True, kw_only=True)
class BatchEntity(BaseEntity):
    is_closed: bool = False
    closed_at: datetime | None = None

    task_description: TaskDescription
    shift: Shift
    team: Team

    batch_number: BatchNumber
    batch_date: date

    nomenclature: Nomenclature
    ekn_code: EknCode

    shift_time_range: ShiftTimeRange

    products: list["ProductEntity"]
    work_center_id: UUID

    def __post_init__(self) -> None:
        if self.is_closed and self.closed_at is None:
            raise InvalidStateError("Время закрытия должно быть установлено для закрытой партии")
        if not self.is_closed and self.closed_at is not None:
            raise InvalidStateError("Время закрытия должно быть пустым для открытой партии")
        if self.products is None:
            self.products = []

    def can_close(self) -> bool:
        """Проверяет, можно ли закрыть партию"""
        if self.is_closed:
            return False
        if not self.products:
            return False
        return all(product.is_aggregated for product in self.products)

    def close(self, closed_at: datetime | None = None) -> None:
        """Закрывает партию с валидацией"""
        if self.is_closed:
            raise InvalidStateError("Партия уже закрыта")
        if closed_at is None:
            closed_at = datetime_now()
        self.is_closed = True
        self.closed_at = closed_at
        self.updated_at = datetime_now()
        self.add_domain_event(
            BatchClosedEvent(aggregate_id=self.uuid, batch_number=self.batch_number, closed_at=closed_at)
        )

    def add_product(self, product: "ProductEntity") -> None:
        """Добавляет продукт в партию"""
        if self.is_closed:
            raise InvalidStateError("Нельзя добавлять продукты в закрытую партию")

        if product.batch_id != self.uuid:
            raise InvalidStateError("Продукт должен принадлежать этой партии")

        if product in self.products:
            raise InvalidStateError("Продукт уже добавлен в партию")

        self.products.append(product)
        self.updated_at = datetime_now()
        self.add_domain_event(
            ProductAddedToBatchEvent(aggregate_id=self.uuid, product_id=product.uuid, batch_id=self.uuid)
        )

    def remove_product(self, product: "ProductEntity") -> None:
        """Удаляет продукт из партии"""
        if self.is_closed:
            raise InvalidStateError("Нельзя удалять продукты из закрытой партии")

        if product not in self.products:
            raise InvalidStateError("Продукт не найден в партии")

        self.products.remove(product)
        self.updated_at = datetime_now()
        self.add_domain_event(
            ProductRemovedFromBatchEvent(aggregate_id=self.uuid, product_id=product.uuid, batch_id=self.uuid)
        )

    def update_shift_time_range(self, start: datetime, end: datetime) -> None:
        """Обновляет временной диапазон смены"""
        if self.is_closed:
            raise InvalidStateError("Нельзя изменять время смены для закрытой партии")
        new_range = ShiftTimeRange(start=start, end=end)
        self.shift_time_range = new_range
        self.updated_at = datetime_now()
