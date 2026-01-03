from typing import Any

from src.application.batches.commands.create import CreateBatchCommand
from src.application.batches.commands.update import UpdateBatchCommand
from src.application.batches.dtos.import_batches import ImportBatchesOutputDTO, ImportRowResult
from src.application.batches.mappers import import_row_to_create_dto, import_row_to_update_dto
from src.application.common.exceptions import FileParseError
from src.application.common.ports import FileParserProtocol
from src.core.logging import get_logger
from src.domain.batches import BatchRepositoryProtocol
from src.domain.batches.services.validate_import_row import BatchImportRowValidator

logger = get_logger("entities.import.service")


class BatchesImportService:
    """
    Application Service для импорта партий из файлов.

    Оркестрирует процесс импорта:
    1. Парсинг файла через Parser
    2. Валидация данных через Domain Validator
    3. Создание/обновление через Commands
    """

    def __init__(
        self,
        parser: FileParserProtocol,
        validator: BatchImportRowValidator,
        create_command: CreateBatchCommand,
        update_command: UpdateBatchCommand,
        repository: BatchRepositoryProtocol,
    ):
        self._parser = parser
        self._validator = validator
        self._create_command = create_command
        self._update_command = update_command
        self._repository = repository

    async def import_batches(self, import_file_data: bytes, update_existing: bool = False) -> ImportBatchesOutputDTO:
        """
        Импортирует партии из файла.

        Args:
            import_file_data: данные файла с сущностями для импорта
            update_existing: обновлять ли существующие сущности

        Returns:
            Результат импорта (total, created, updated, failed, errors)
        """
        logger.info(f"Starting import: update_existing={update_existing}")

        # 1. Парсинг файла
        try:
            raw_data: list[dict[str, Any]] = await self._parser.parse(import_file_data)
        except FileParseError as e:
            logger.error(f"File parsing failed: {e}")
            return ImportBatchesOutputDTO(
                total=0, created=0, updated=0, failed=0, errors=[{"row": 0, "error": f"Ошибка парсинга файла: {e}"}]
            )

        if not raw_data:
            logger.warning("No data found in file")
            return ImportBatchesOutputDTO(total=0, created=0, updated=0, failed=0, errors=[])

        # 2. Обработка каждой строки
        total = len(raw_data)
        created_count = 0
        updated_count = 0
        failed_count = 0
        errors: list[dict[str, Any]] = []

        for row_number, row in enumerate(raw_data, start=1):
            try:
                result = await self._process_row(row, update_existing=update_existing)

                if result.created:
                    created_count += 1
                elif result.updated:
                    updated_count += 1
                else:
                    failed_count += 1
                    errors.append({"row": row_number, "error": result.error or "Unknown error"})

            except Exception as e:
                logger.exception(f"Error processing row {row_number}: {e}")
                failed_count += 1
                errors.append({"row": row_number, "error": str(e)})

        logger.info(
            f"Import completed: total={total}, created={created_count}, updated={updated_count}, failed={failed_count}"
        )

        return ImportBatchesOutputDTO(
            total=total, created=created_count, updated=updated_count, failed=failed_count, errors=errors
        )

    async def _process_row(self, row_data: dict[str, Any], update_existing: bool = False) -> ImportRowResult:
        """
        Обрабатывает одну строку данных.

        Returns:
            Результат обработки строки
        """
        # 1. Валидация через Domain Validator (создает BatchImportRow внутри)
        validation_result = await self._validator.validate(row_data=row_data, update_existing=update_existing)

        if not validation_result.is_valid:
            return ImportRowResult(created=False, updated=False, error="; ".join(validation_result.errors))

        # validation_result.validated_row содержит BatchImportRow после успешной валидации
        import_row = validation_result.validated_row
        if import_row is None:
            return ImportRowResult(created=False, updated=False, error="Ошибка валидации: validated_row is None")

        # 2. Преобразование в DTO
        if update_existing:
            # Проверка существования партии
            existing_batch = await self._repository.get_by_batch_number_and_date(
                import_row.batch_number.value, import_row.batch_date
            )

            if existing_batch:
                # Обновление
                update_dto = import_row_to_update_dto(import_row, existing_batch.uuid)
                await self._update_command.execute(update_dto)
                return ImportRowResult(created=False, updated=True, error=None)

        # Создание новой партии
        create_dto = import_row_to_create_dto(import_row)
        await self._create_command.execute(create_dto)

        return ImportRowResult(created=True, updated=False, error=None)
