from dataclasses import dataclass
from datetime import date, datetime
from typing import TYPE_CHECKING

from src.domain.shared.entity import BaseEntity
from src.domain.shared.exceptions import (
    EmptyFieldError,
    InvalidDateRangeError,
    InvalidStateError,
    InvalidValueError,
)

if TYPE_CHECKING:
    from src.domain.product.entity import ProductEntity
    from src.domain.work_center.entity import WorkCenterEntity


@dataclass(frozen=True, slots=True, kw_only=True)
class BatchEntity(BaseEntity):
    is_closed: bool = False
    closed_at: datetime | None = None

    task_description: str
    shift: str
    team: str

    batch_number: int
    batch_date: date

    nomenclature: str
    ekn_code: str

    shift_start: datetime
    shift_end: datetime

    products: list["ProductEntity"]
    work_center: "WorkCenterEntity"

    def __post_init__(self) -> None:
        if not self.task_description or not self.task_description.strip():
            raise EmptyFieldError("Описание задачи не может быть пустым")
        if not self.shift or not self.shift.strip():
            raise EmptyFieldError("Смена не может быть пустой")
        if not self.team or not self.team.strip():
            raise EmptyFieldError("Бригада не может быть пустой")
        if not self.nomenclature or not self.nomenclature.strip():
            raise EmptyFieldError("Номенклатура не может быть пустой")
        if not self.ekn_code or not self.ekn_code.strip():
            raise EmptyFieldError("Код ЕКН не может быть пустым")
        if self.batch_number <= 0:
            raise InvalidValueError("Номер партии должен быть положительным числом")
        if self.shift_end <= self.shift_start:
            raise InvalidDateRangeError("Время окончания смены должно быть позже времени начала")
        if self.is_closed and self.closed_at is None:
            raise InvalidStateError("Время закрытия должно быть установлено для закрытой партии")
        if not self.is_closed and self.closed_at is not None:
            raise InvalidStateError("Время закрытия должно быть пустым для открытой партии")
