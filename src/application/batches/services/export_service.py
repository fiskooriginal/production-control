from uuid import uuid4

from src.application.batches.dtos.export_batches import ExportBatchesInputDTO, ExportBatchesOutputDTO
from src.application.batches.mappers import entity_to_raw_data_dto
from src.application.batches.queries.queries import ListBatchesQuery
from src.application.batches.queries.service import BatchQueryServiceProtocol
from src.application.common.exceptions import ApplicationException
from src.application.common.ports.file_generator import FileGeneratorProtocol
from src.application.common.storage.interfaces import StorageServiceProtocol
from src.application.work_centers.queries.queries import ListWorkCentersQuery
from src.application.work_centers.queries.service import WorkCenterQueryServiceProtocol
from src.core.logging import get_logger

logger = get_logger("entities.export.service")


def generate_file_name(file_extension: str) -> str:
    """Генерирует имя файла с timestamp."""
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_id = str(uuid4())[:8]

    return f"batches/{timestamp}_{file_id}.{file_extension}"


class BatchesExportService:
    """
    Application Service для экспорта партий в файлы.

    Оркестрирует процесс экспорта:
    1. Получение данных через Query Service
    2. Генерация файла через Generator
    3. Сохранение в Storage
    """

    EXPORT_BUCKET = "exports"

    def __init__(
        self,
        query_service: BatchQueryServiceProtocol,
        work_center_query_service: WorkCenterQueryServiceProtocol,
        generator: FileGeneratorProtocol,
        storage_service: StorageServiceProtocol,
    ):
        self._query_service = query_service
        self._work_center_query_service = work_center_query_service
        self._generator = generator
        self._storage_service = storage_service

    async def export_batches(self, input_dto: ExportBatchesInputDTO) -> ExportBatchesOutputDTO:
        """
        Экспортирует партии в файл.

        Args:
            input_dto: Параметры экспорта (формат, фильтры)

        Returns:
            Результат экспорта (URL файла, количество партий)

        Raises:
            ExportError: При ошибке экспорта
        """
        logger.info(f"Starting export: format={input_dto.format}, filters={input_dto.filters}")

        try:
            # 1. Получение данных через Query Service
            query = ListBatchesQuery(filters=input_dto.filters)
            result = await self._query_service.list(query)
            batches = result.items

            if not batches:
                logger.warning("No entities found for export")
                return ExportBatchesOutputDTO(file_url="", total_batches=0)

            # 2. Загрузка рабочих центров
            query = ListWorkCentersQuery()
            result = await self._work_center_query_service.list(query)
            work_centers = result.items

            # 3. Генерация файла
            work_centers_by_id = {work_center.uuid: work_center for work_center in work_centers}
            raw_data = [entity_to_raw_data_dto(batch, work_centers_by_id[batch.work_center_id]) for batch in batches]
            file_data = await self._generator.generate(raw_data)

            # 4. Сохранение в Storage
            file_name = generate_file_name(str(input_dto.format))
            file_url = await self._storage_service.upload_file(
                bucket_name=self.EXPORT_BUCKET,
                object_name=file_name,
                file_data=file_data,
                file_extension=input_dto.format,
            )

            presigned_url = await self._storage_service.get_presigned_url(
                bucket_name=self.EXPORT_BUCKET, object_name=file_url, expires_seconds=3600
            )

            logger.info(f"Export completed: file_url={file_url}, total_batches={len(batches)}")
            return ExportBatchesOutputDTO(file_url=file_url, presigned_url=presigned_url, total_batches=len(batches))

        except Exception as e:
            logger.exception(f"Export failed: {e}")
            raise ApplicationException(f"Ошибка экспорта: {e}") from e
