from dataclasses import dataclass

from src.domain.common.exceptions import InvalidValueError
from src.domain.common.value_objects import ValueObject


@dataclass(frozen=True, slots=True)
class Timeout(ValueObject):
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise InvalidValueError("Таймаут должен быть > 0")

    def __str__(self) -> str:
        return str(self.value)
