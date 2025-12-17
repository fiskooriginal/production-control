from dataclasses import dataclass

from src.domain.shared.entities import BaseEntity
from src.domain.shared.exceptions import EmptyFieldError


@dataclass(frozen=True, slots=True, kw_only=True)
class WorkCenterEntity(BaseEntity):
    identifier: str
    name: str

    def __post_init__(self) -> None:
        if not self.identifier or not self.identifier.strip():
            raise EmptyFieldError("Идентификатор рабочего центра не может быть пустым")
        if not self.name or not self.name.strip():
            raise EmptyFieldError("Название рабочего центра не может быть пустым")
