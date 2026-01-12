from dataclasses import dataclass
from datetime import datetime

from src.domain.common.exceptions import InvalidDateRangeError
from src.domain.common.value_objects import ValueObject


@dataclass(frozen=True, slots=True)
class ShiftTimeRange(ValueObject):
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.end <= self.start:
            raise InvalidDateRangeError("Время окончания смены должно быть позже времени начала")

    def __str__(self) -> str:
        return f"{self.start} - {self.end}"
