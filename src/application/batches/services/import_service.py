import json

from typing import Any

from src.application.batches.commands.add_product import AddProductToBatchCommand
from src.application.batches.commands.create import CreateBatchCommand
from src.application.batches.commands.update import UpdateBatchCommand
from src.application.batches.dtos.import_batches import ImportBatchesOutputDTO, ImportRowResult
from src.application.batches.dtos.raw_data import ProductRawDataDTO
from src.application.batches.mappers import import_row_to_create_dto, import_row_to_update_dto
from src.application.common.exceptions import FileParseError
from src.application.common.ports.file_parser import FileParserProtocol
from src.application.work_centers.commands.create import CreateWorkCenterCommand
from src.application.work_centers.dtos.create import CreateWorkCenterInputDTO
from src.core.logging import get_logger
from src.domain.batches.interfaces.repository import BatchRepositoryProtocol
from src.domain.batches.services import BatchImportRowValidator
from src.domain.common.exceptions import AlreadyExistsError
from src.domain.work_centers.interfaces.repository import WorkCenterRepositoryProtocol

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
        add_product_command: AddProductToBatchCommand,
        create_work_center_command: CreateWorkCenterCommand,
        work_center_repository: WorkCenterRepositoryProtocol,
        batch_repository: BatchRepositoryProtocol,
    ):
        self._parser = parser
        self._validator = validator
        self._create_command = create_command
        self._update_command = update_command
        self._add_product_command = add_product_command
        self._create_work_center_command = create_work_center_command
        self._work_center_repository = work_center_repository
        self._batch_repository = batch_repository

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

        # 2. Поиск или создание рабочего центра
        work_center = await self._work_center_repository.get_by_identifier(import_row.work_center_identifier)
        if work_center is None:
            # Создание рабочего центра с дефолтным именем
            create_work_center_dto = CreateWorkCenterInputDTO(
                identifier=import_row.work_center_identifier, name=import_row.work_center_name
            )
            work_center = await self._create_work_center_command.execute(create_work_center_dto)
            logger.info(f"Created work center: identifier={import_row.work_center_identifier}")

        work_center_id = work_center.uuid

        # 3. Преобразование в DTO и создание/обновление партии
        batch_entity = None
        if update_existing:
            # Проверка существования партии
            existing_batch = await self._batch_repository.get_by_batch_number_and_date(
                str(import_row.batch_number), import_row.batch_date
            )

            if existing_batch:
                # Обновление
                update_dto = import_row_to_update_dto(import_row, existing_batch.uuid, work_center_id)
                batch_entity = await self._update_command.execute(update_dto)
                result = ImportRowResult(created=False, updated=True, error=None)
            else:
                # Создание новой партии
                create_dto = import_row_to_create_dto(import_row, work_center_id)
                batch_entity = await self._create_command.execute(create_dto)
                result = ImportRowResult(created=True, updated=False, error=None)
        else:
            # Создание новой партии
            create_dto = import_row_to_create_dto(import_row, work_center_id)
            batch_entity = await self._create_command.execute(create_dto)
            result = ImportRowResult(created=True, updated=False, error=None)

        # 4. Импорт продуктов из JSON поля products
        if batch_entity:
            products_json = row_data.get("products", "[]")
            if products_json:
                try:
                    products_data = json.loads(products_json) if isinstance(products_json, str) else products_json

                    if isinstance(products_data, list):
                        for product_data in products_data:
                            try:
                                product_dto = ProductRawDataDTO(**product_data)
                                await self._add_product_command.execute(
                                    batch_id=batch_entity.uuid, unique_code=product_dto.unique_code
                                )
                            except AlreadyExistsError:
                                logger.warning(
                                    f"Product with code {product_dto.unique_code} already exists in batch {batch_entity.uuid}, skipping"
                                )
                                continue
                            except Exception as e:
                                logger.warning(f"Failed to add product {product_dto.unique_code}: {e}, skipping")
                                continue
                except (json.JSONDecodeError, ValueError, TypeError) as e:
                    logger.warning(f"Failed to parse products JSON: {e}")

        return result
