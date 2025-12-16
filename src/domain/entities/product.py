from dataclasses import dataclass
from datetime import datetime

from src.domain.shared.entity import BaseEntity
from src.domain.shared.exceptions import EmptyFieldError, InvalidStateError


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductEntity(BaseEntity):
    unique_code: str
    is_aggregated: bool = False
    aggregated_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.unique_code or not self.unique_code.strip():
            raise EmptyFieldError("Уникальный код не может быть пустым")
        if self.is_aggregated and self.aggregated_at is None:
            raise InvalidStateError("Время агрегации должно быть установлено для агрегированного продукта")
        if not self.is_aggregated and self.aggregated_at is not None:
            raise InvalidStateError("Время агрегации должно быть пустым для неагрегированного продукта")
