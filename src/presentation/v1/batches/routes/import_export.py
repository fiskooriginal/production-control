import base64

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from src.application.common.dtos import ExportImportFileFormatEnum
from src.infrastructure.background_tasks import states
from src.infrastructure.background_tasks.tasks import export_batches as export_batches_task
from src.infrastructure.background_tasks.tasks import import_batches as import_batches_task
from src.presentation.exceptions.base import PresentationException
from src.presentation.v1.background_tasks.schemas import TaskStartedResponse
from src.presentation.v1.batches.mappers import batch_filters_params_to_query
from src.presentation.v1.batches.schemas.filters import BatchFiltersParams

router = APIRouter()


@router.post("/import", response_model=TaskStartedResponse, status_code=status.HTTP_202_ACCEPTED)
async def import_batches(
    file: UploadFile = File(..., description="Файл с партиями (xlsx/csv)"),
    update_existing: bool = False,
) -> TaskStartedResponse:
    """
    Импортирует партии из файла.

    Импорт выполняется асинхронно в фоновой задаче.
    """
    file_extension = file.filename.split(".")[-1].lower() if file.filename else ""

    allowed_extensions = [fmt.value for fmt in ExportImportFileFormatEnum]

    if file_extension not in allowed_extensions:
        raise PresentationException(
            f"Unsupported file format: {file_extension}. Supported formats: {', '.join(allowed_extensions)}"
        )

    file_data = await file.read()
    file_data_base64 = base64.b64encode(file_data).decode("utf-8")

    task = import_batches_task.delay(
        file_data_base64=file_data_base64, file_extension=file_extension, update_existing=update_existing
    )

    return TaskStartedResponse(
        task_id=task.id,
        status=states.PENDING,
        message="Import task started",
    )


@router.post("/export", response_model=TaskStartedResponse, status_code=status.HTTP_202_ACCEPTED)
async def export_batches(
    format: ExportImportFileFormatEnum = Query(..., description="Формат экспорта"),
    filters: BatchFiltersParams = Depends(),
) -> TaskStartedResponse:
    """
    Экспортирует партии в файл.

    Экспорт выполняется асинхронно в фоновой задаче.
    """
    filters = batch_filters_params_to_query(filters, return_none=False)
    task = export_batches_task.delay(format=format, filters=filters)

    return TaskStartedResponse(
        task_id=task.id,
        status=states.PENDING,
        message="Export task started",
    )
