from dataclasses import dataclass

from src.domain.common.exceptions import EmptyFieldError
from src.domain.common.value_objects import ValueObject


@dataclass(frozen=True, slots=True)
class ProductCode(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise EmptyFieldError("Уникальный код не может быть пустым")

    def __str__(self) -> str:
        return self.value
