import base64

from uuid import UUID

from sqlalchemy.exc import DBAPIError, OperationalError

from src.application.batches.commands.add_product import AddProductToBatchCommand
from src.application.batches.commands.create import CreateBatchCommand
from src.application.batches.commands.update import UpdateBatchCommand
from src.application.batches.services.import_service import BatchesImportService
from src.application.common.exceptions import FileParseError
from src.application.work_centers.commands.create import CreateWorkCenterCommand
from src.core.logging import get_logger
from src.core.settings import CelerySettings
from src.domain.batches.events import BatchesImportCompletedEvent
from src.domain.batches.services import BatchImportRowValidator
from src.infrastructure.background_tasks.app import celery_app, get_session_factory, run_async_task
from src.infrastructure.common.file_parsers import FileParserFactory
from src.infrastructure.common.uow.unit_of_work import SqlAlchemyUnitOfWork

logger = get_logger("celery.tasks.import_batches")

celery_settings = CelerySettings()


def _is_retryable_error(exception: Exception) -> bool:
    """Проверяет, является ли ошибка повторяемой (retryable)"""
    return isinstance(exception, (OperationalError, DBAPIError))


@celery_app.task(bind=True, max_retries=None)
def import_batches(
    self,
    file_data_base64: str,
    file_extension: str,
    update_existing: bool = False,
) -> dict:
    """
    Асинхронный импорт партий из файла.

    Args:
        file_data_base64: Байты файла в формате base64
        file_extension: Расширение файла (xlsx, csv)
        update_existing: Обновлять ли существующие партии

    Returns:
        {
            "success": True,
            "total": 100,
            "created": 80,
            "updated": 15,
            "failed": 5,
            "errors": [
                {"row": 10, "error": "Validation error"},
                ...
            ]
        }
    """
    try:
        file_data = base64.b64decode(file_data_base64)
    except Exception as e:
        logger.error(f"Failed to decode base64 file data: {e}")
        raise ValueError(f"Invalid base64 file data: {e}") from e

    return run_async_task(_import_batches_async(self, file_data, file_extension, update_existing))


async def _import_batches_async(
    task_instance,
    file_data: bytes,
    file_extension: str,
    update_existing: bool,
) -> dict:
    """Асинхронная часть задачи импорта"""
    session_factory = get_session_factory()

    try:
        async with session_factory() as session:
            uow = SqlAlchemyUnitOfWork(session, manual_commit=True)

            async with uow:
                # Создание зависимостей
                parser = FileParserFactory.create(file_extension)
                validator = BatchImportRowValidator(uow.batches, uow.work_centers)
                create_command = CreateBatchCommand(uow)
                update_command = UpdateBatchCommand(uow)
                add_product_command = AddProductToBatchCommand(uow)
                create_work_center_command = CreateWorkCenterCommand(uow)

                # Создание сервиса импорта
                import_service = BatchesImportService(
                    parser=parser,
                    validator=validator,
                    create_command=create_command,
                    update_command=update_command,
                    add_product_command=add_product_command,
                    create_work_center_command=create_work_center_command,
                    work_center_repository=uow.work_centers,
                    batch_repository=uow.batches,
                )

                # Запуск импорта
                result = await import_service.import_batches(file_data, update_existing)

                # Регистрация события о завершении импорта
                uow.register_event(
                    BatchesImportCompletedEvent(
                        aggregate_id=UUID(task_instance.request.id),
                        task_id=UUID(task_instance.request.id),
                        update_existing=update_existing,
                        total_rows=result.total,
                        created=result.created,
                        updated=result.updated,
                        skipped=result.failed,
                        errors=result.errors,
                    )
                )

                await uow.commit()

                logger.info(
                    f"Import completed: total={result.total}, created={result.created}, "
                    f"updated={result.updated}, failed={result.failed}"
                )

                return {
                    "success": True,
                    "total": result.total,
                    "created": result.created,
                    "updated": result.updated,
                    "failed": result.failed,
                    "errors": result.errors,
                }

    except FileParseError as e:
        logger.error(f"File parsing failed: {e}")
        return {
            "success": False,
            "total": 0,
            "created": 0,
            "updated": 0,
            "failed": 0,
            "errors": [{"row": 0, "error": f"Ошибка парсинга файла: {e}"}],
        }
    except Exception as e:
        logger.exception(f"Failed to import batches: {e}")
        if _is_retryable_error(e) and task_instance.request.retries < celery_settings.task_max_retries:
            raise task_instance.retry(
                exc=e,
                countdown=celery_settings.task_default_retry_delay,
            ) from e
        raise
