from dataclasses import dataclass

from src.domain.common.exceptions import InvalidValueError
from src.domain.common.value_objects import ValueObject


@dataclass(frozen=True, slots=True)
class HttpStatusCode(ValueObject):
    value: int

    def __post_init__(self) -> None:
        if not (100 <= self.value <= 599):
            raise InvalidValueError("HTTP статус должен быть в диапазоне 100-599")

    def __str__(self) -> str:
        return str(self.value)
