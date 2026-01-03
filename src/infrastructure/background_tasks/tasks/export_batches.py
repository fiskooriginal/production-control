from datetime import datetime
from uuid import uuid4

from sqlalchemy.exc import DBAPIError, OperationalError

from src.application.batches.mappers import entity_to_raw_data_dto
from src.application.batches.queries.queries import ListBatchesQuery
from src.application.common.dtos import ExportImportFileFormatEnum
from src.core.logging import get_logger
from src.core.settings import CelerySettings
from src.infrastructure.background_tasks.app import celery_app, get_session_factory, get_storage_service, run_async_task
from src.infrastructure.common.file_generators.batches.exports.factory import BatchesExportGeneratorFactory
from src.infrastructure.persistence.queries import BatchQueryService
from src.presentation.api.schemas.batches import BatchFiltersParams
from src.presentation.mappers.query_params import batch_filters_params_to_query

logger = get_logger("celery.tasks.export_batches")

celery_settings = CelerySettings()


def _is_retryable_error(exception: Exception) -> bool:
    """Проверяет, является ли ошибка повторяемой (retryable)"""
    return isinstance(exception, (OperationalError, DBAPIError))


@celery_app.task(bind=True, max_retries=None)
def export_batches(
    self,
    format: ExportImportFileFormatEnum,
    filters: BatchFiltersParams,
) -> dict:
    """
    Асинхронный экспорт партий в файл (XLSX или CSV).

    Args:
        format: Формат файла (xlsx или csv)
        filters: Параметры фильтрации партий

    Returns:
        {
            "success": True,
            "file_path": "exports/...",
            "download_url": "https://...",
            "total": 100
        }
    """
    return run_async_task(_export_batches_async(self, format, filters))


async def _export_batches_async(
    task_instance,
    format: ExportImportFileFormatEnum,
    filters: BatchFiltersParams,
) -> dict:
    """Асинхронная часть задачи экспорта"""
    session_factory = get_session_factory()
    storage_service = get_storage_service()

    try:
        async with session_factory() as session:
            query_service = BatchQueryService(session)

            try:
                filters = batch_filters_params_to_query(filters)
            except Exception as e:
                logger.warning(f"Failed to parse filters: {e}, using empty filters")
                filters = None

            query = ListBatchesQuery(filters=filters, pagination=None, sort=None)
            result = await query_service.list(query)
            batches = result.items
            logger.info(f"Exporting {len(batches)} batches to {format} file")

            file_extension = str(format)
            generator = BatchesExportGeneratorFactory.create(file_extension)

            file_content = await generator.generate(raw_data=[entity_to_raw_data_dto(batch) for batch in batches])

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_id = str(uuid4())[:8]
            object_name = f"batches/{timestamp}_{file_id}.{file_extension}"

            await storage_service.upload_file(
                bucket_name="exports", object_name=object_name, file_data=file_content, file_extension=file_extension
            )

            download_url = await storage_service.get_presigned_url(
                bucket_name="exports", object_name=object_name, expires_seconds=3600
            )

            logger.info(f"Export completed: {len(batches)} batches exported to {object_name}")

            return {
                "success": True,
                "file_path": object_name,
                "download_url": download_url,
                "total": len(batches),
            }

    except Exception as e:
        logger.exception(f"Failed to export batches: {e}")
        if _is_retryable_error(e) and task_instance.request.retries < celery_settings.task_max_retries:
            raise task_instance.retry(
                exc=e,
                countdown=celery_settings.task_default_retry_delay,
            ) from e
        raise
