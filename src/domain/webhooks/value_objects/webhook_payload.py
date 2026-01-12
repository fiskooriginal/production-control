from dataclasses import dataclass
from typing import Any

from src.domain.common.exceptions import EmptyFieldError
from src.domain.common.value_objects import ValueObject


@dataclass(frozen=True, slots=True)
class WebhookPayload(ValueObject):
    value: dict[str, Any]

    def __post_init__(self) -> None:
        if not self.value:
            raise EmptyFieldError("Полезная нагрузка не может быть пустой")

    def __str__(self) -> str:
        return str(self.value)
