from dataclasses import dataclass
from typing import Any

from src.core.logging import get_logger
from src.domain.batches.interfaces.repository import BatchRepositoryProtocol
from src.domain.batches.services.validate_batch_uniqueness import validate_batch_uniqueness
from src.domain.batches.value_objects.import_row import BatchImportRow
from src.domain.common.exceptions import DoesNotExistError
from src.domain.work_centers.interfaces.repository import WorkCenterRepositoryProtocol

logger = get_logger("entities.import.validator")


@dataclass(frozen=True)
class ValidationResult:
    """Результат валидации строки импорта."""

    is_valid: bool
    errors: list[str]
    validated_row: BatchImportRow | None = None


class BatchImportRowValidator:
    """
    Domain Service для валидации данных импорта партий.

    Валидирует бизнес-правила:
    - Существование work_center
    - Уникальность batch_number + batch_date (если update_existing=False)
    - Валидность временных диапазонов
    """

    def __init__(
        self,
        batch_repository: BatchRepositoryProtocol,
        work_center_repository: WorkCenterRepositoryProtocol,
    ):
        self._batch_repository = batch_repository
        self._work_center_repository = work_center_repository

    async def validate(
        self,
        row_data: dict[str, Any],
        update_existing: bool = False,
    ) -> ValidationResult:
        """
        Валидирует одну строку данных импорта.

        Args:
            row_data: Словарь с данными партии
            update_existing: Если True, разрешает обновление существующих партий

        Returns:
            Результат валидации с ошибками (если есть)
        """
        errors: list[str] = []

        # 1. Валидация форматов через Value Object
        try:
            import_row = BatchImportRow.from_dict(row_data)
            format_errors = import_row.validate_formats()
            if format_errors:
                errors.extend(format_errors)
        except Exception as e:
            errors.append(f"Ошибка валидации форматов: {e}")
            return ValidationResult(is_valid=False, errors=errors)

        # 2. Проверка существования work_center
        try:
            await self._work_center_repository.get_or_raise(import_row.work_center_id)
        except DoesNotExistError:
            errors.append(f"Рабочий центр '{import_row.work_center_id}' не найден")

        # 3. Проверка уникальности (если не обновление)
        if not update_existing:
            exists = await validate_batch_uniqueness(
                batch_number=import_row.batch_number,
                batch_date=import_row.batch_date,
                repository=self._batch_repository,
            )
            if exists:
                errors.append(
                    f"Партия с номером {import_row.batch_number.value} и датой {import_row.batch_date} уже существует"
                )

        if errors:
            return ValidationResult(
                is_valid=False,
                errors=errors,
                validated_row=None,
            )

        return ValidationResult(
            is_valid=True,
            errors=[],
            validated_row=import_row,
        )
