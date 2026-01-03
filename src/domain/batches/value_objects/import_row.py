from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from src.domain.batches import ShiftTimeRange
from src.domain.batches.value_objects import (
    BatchNumber,
    EknCode,
    Nomenclature,
    Shift,
    TaskDescription,
    Team,
)


@dataclass(frozen=True, slots=True)
class BatchImportRow:
    """
    Value Object для валидации строки импорта партии.

    Инкапсулирует валидацию форматов данных.
    """

    batch_number: BatchNumber
    batch_date: date
    nomenclature: Nomenclature
    ekn_code: EknCode
    task_description: TaskDescription
    shift: Shift
    team: Team
    shift_time_range: ShiftTimeRange
    is_closed: bool
    closed_at: datetime | None
    work_center_identifier: str
    work_center_name: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BatchImportRow":
        """
        Создает BatchImportRow из словаря с валидацией.

        Raises:
            ValueError: При неверных форматах данных
        """
        try:
            return cls(
                batch_number=BatchNumber(int(data["batch_number"])),
                batch_date=cls._parse_date(data["batch_date"]),
                nomenclature=Nomenclature(data["nomenclature"]),
                ekn_code=EknCode(data["ekn_code"]),
                task_description=TaskDescription(data["task_description"]),
                shift=Shift(data["shift"]),
                team=Team(data["team"]),
                shift_time_range=ShiftTimeRange(
                    start=cls._parse_datetime(data["shift_start"]),
                    end=cls._parse_datetime(data["shift_end"]),
                ),
                is_closed=bool(data.get("is_closed", False)),
                closed_at=cls._parse_datetime(data.get("closed_at")) if data.get("closed_at") else None,
                work_center_identifier=str(data["work_center_identifier"]),
                work_center_name=str(data["work_center_name"]),
            )
        except (KeyError, ValueError, TypeError) as e:
            raise ValueError(f"Ошибка создания BatchImportRow: {e}") from e

    def validate_formats(self) -> list[str]:
        """
        Валидирует форматы данных.

        Returns:
            Список ошибок (пустой, если все валидно)
        """
        errors: list[str] = []

        # Валидация временных диапазонов
        if self.shift_time_range.start >= self.shift_time_range.end:
            errors.append("Время начала смены должно быть раньше времени окончания")

        # Валидация closed_at
        if self.is_closed and self.closed_at is None:
            errors.append("Для закрытой партии должно быть указано время закрытия")

        if not self.is_closed and self.closed_at is not None:
            errors.append("Для открытой партии не должно быть времени закрытия")

        return errors

    @staticmethod
    def _parse_date(value: Any) -> date:
        """Парсит дату из различных форматов."""
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            # Попытка ISO формата
            try:
                return date.fromisoformat(value)
            except ValueError as e:
                # Попытка других форматов
                from datetime import datetime as dt

                for fmt in ["%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"]:
                    try:
                        return dt.strptime(value, fmt).date()
                    except ValueError:
                        continue
                raise ValueError(f"Неверный формат даты: {value}") from e
        raise ValueError(f"Неверный тип для даты: {type(value)}")

    @staticmethod
    def _parse_datetime(value: Any) -> datetime:
        """Парсит datetime из различных форматов."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            # Попытка ISO формата
            try:
                return datetime.fromisoformat(value)
            except ValueError as e:
                # Попытка других форматов
                for fmt in [
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S",
                    "%d.%m.%Y %H:%M:%S",
                ]:
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue
                raise ValueError(f"Неверный формат datetime: {value}") from e
        raise ValueError(f"Неверный тип для datetime: {type(value)}")
