from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ValueObject:
    """Базовый класс для Value Objects"""

    def __str__(self) -> str:
        return str(self.__dict__.values().__iter__().__next__()) if self.__dict__ else ""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(f'{k}={v!r}' for k, v in self.__dict__.items())})"
