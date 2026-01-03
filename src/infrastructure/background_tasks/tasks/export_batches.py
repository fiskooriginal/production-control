from sqlalchemy.exc import DBAPIError, OperationalError

from src.application.batches.dtos.export_batches import ExportBatchesInputDTO
from src.application.batches.services.export_service import BatchesExportService
from src.application.common.dtos import ExportImportFileFormatEnum
from src.core.logging import get_logger
from src.core.settings import CelerySettings
from src.infrastructure.background_tasks.app import celery_app, get_session_factory, get_storage_service, run_async_task
from src.infrastructure.common.file_generators.batches.exports.factory import BatchesExportGeneratorFactory
from src.infrastructure.persistence.queries import BatchQueryService, WorkCenterQueryService
from src.presentation.api.schemas.batches import BatchFiltersParams

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
            work_center_query_service = WorkCenterQueryService(session)
            generator = BatchesExportGeneratorFactory.create(str(format))

            export_service = BatchesExportService(
                query_service=query_service,
                work_center_query_service=work_center_query_service,
                generator=generator,
                storage_service=storage_service,
            )
            input_dto = ExportBatchesInputDTO(format=format, filters=filters)
            try:
                result = await export_service.export_batches(input_dto)
            except Exception as e:
                logger.exception(f"Failed to export batches: {e}")
                raise task_instance.retry(
                    exc=e,
                    countdown=celery_settings.task_default_retry_delay,
                ) from e

            logger.info(f"Export completed: {result.total_batches} batches exported to {result.file_url}")
            return {
                "success": True,
                "file_path": result.file_url,
                "download_url": result.presigned_url,
                "total": result.total_batches,
            }

    except Exception as e:
        logger.exception(f"Failed to export batches: {e}")
        if _is_retryable_error(e) and task_instance.request.retries < celery_settings.task_max_retries:
            raise task_instance.retry(
                exc=e,
                countdown=celery_settings.task_default_retry_delay,
            ) from e
        raise
