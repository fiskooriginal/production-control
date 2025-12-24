from dataclasses import dataclass
from datetime import datetime

from src.domain.shared.exceptions import EmptyFieldError, InvalidDateRangeError, InvalidValueError
from src.domain.shared.value_objects import ValueObject


@dataclass(frozen=True, slots=True)
class BatchNumber(ValueObject):
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise InvalidValueError("Номер партии должен быть положительным числом")

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class TaskDescription(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise EmptyFieldError("Описание задачи не может быть пустым")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class Shift(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise EmptyFieldError("Смена не может быть пустой")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class Team(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise EmptyFieldError("Бригада не может быть пустой")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class Nomenclature(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise EmptyFieldError("Номенклатура не может быть пустой")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class EknCode(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise EmptyFieldError("Код ЕКН не может быть пустым")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ShiftTimeRange(ValueObject):
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.end <= self.start:
            raise InvalidDateRangeError("Время окончания смены должно быть позже времени начала")

    def __str__(self) -> str:
        return f"{self.start} - {self.end}"
