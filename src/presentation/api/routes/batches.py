import base64

from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from src.application.batches.dtos.generate_report import GenerateReportInputDTO
from src.application.batches.reports.dtos import ReportFormatEnum
from src.application.common.dtos import ExportImportFileFormatEnum
from src.infrastructure.background_tasks import states
from src.infrastructure.background_tasks.tasks import aggregate_batch as aggregate_batch_task
from src.infrastructure.background_tasks.tasks import export_batches as export_batches_task
from src.infrastructure.background_tasks.tasks import import_batches as import_batches_task
from src.presentation.api.schemas.background_tasks import TaskStartedResponse
from src.presentation.api.schemas.batches import (
    AddProductToBatchRequest,
    AggregateBatchRequest,
    AggregateBatchTaskRequest,
    BatchFiltersParams,
    BatchResponse,
    CloseBatchRequest,
    CreateBatchRequest,
    GenerateReportResponse,
    ListBatchesResponse,
    UpdateBatchRequest,
)
from src.presentation.api.schemas.query_params import PaginationParams, SortParams
from src.presentation.di.batches import (
    add_product_to_batch,
    aggregate_batch,
    close_batch,
    create_batch,
    delete_batch,
    get_batch,
    list_batches,
    remove_product_from_batch,
    update_batch,
)
from src.presentation.di.reports import generate_report_command
from src.presentation.mappers.batches import (
    aggregate_batch_request_to_input_dto,
    close_batch_request_to_input_dto,
    create_batch_request_to_input_dto,
    domain_to_response,
    update_batch_request_to_input_dto,
)
from src.presentation.mappers.query_params import build_list_batches_query

router = APIRouter(prefix="/api/batches", tags=["batches"])


@router.post("", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
async def create_batch(request: CreateBatchRequest, command: create_batch) -> BatchResponse:
    """
    Создает новую партию.
    """
    input_dto = create_batch_request_to_input_dto(request)
    batch_entity = await command.execute(input_dto)
    return domain_to_response(batch_entity)


@router.patch("/{batch_id}/close", response_model=BatchResponse)
async def close_batch(batch_id: UUID, request: CloseBatchRequest, command: close_batch) -> BatchResponse:
    """
    Закрывает партию.
    """
    input_dto = close_batch_request_to_input_dto(batch_id, request)
    batch_entity = await command.execute(input_dto)
    return domain_to_response(batch_entity)


@router.post("/{batch_id}/products", response_model=BatchResponse)
async def add_product_to_batch(
    batch_id: UUID, request: AddProductToBatchRequest, command: add_product_to_batch
) -> BatchResponse:
    """
    Добавляет продукт в партию.
    """
    batch_entity = await command.execute(batch_id, request.unique_code)
    return domain_to_response(batch_entity)


@router.delete("/{batch_id}/products/{product_id}", response_model=BatchResponse)
async def remove_product_from_batch(
    batch_id: UUID, product_id: UUID, command: remove_product_from_batch
) -> BatchResponse:
    """
    Удаляет продукт из партии.

    ВАЖНО: Продукт будет полностью удален из БД, так как batch_id NOT NULL.
    """
    batch_entity = await command.execute(batch_id, product_id)
    return domain_to_response(batch_entity)


@router.get("", response_model=ListBatchesResponse)
async def list_batches(
    query_handler: list_batches,
    filter_params: BatchFiltersParams = Depends(),
    pagination_params: PaginationParams = Depends(),
    sort_params: SortParams = Depends(),
) -> ListBatchesResponse:
    """
    Получает список партий с фильтрацией, пагинацией и сортировкой.
    """
    query = build_list_batches_query(filter_params, pagination_params, sort_params)
    result = await query_handler.execute(query)

    return ListBatchesResponse(
        items=[domain_to_response(dto) for dto in result.items],
        total=result.total,
        limit=result.limit,
        offset=result.offset,
    )


@router.get("/{batch_id}", response_model=BatchResponse)
async def get_batch(batch_id: UUID, query_handler: get_batch) -> BatchResponse:
    """
    Получает партию по UUID.
    """
    batch_dto = await query_handler.execute(batch_id)
    return domain_to_response(batch_dto)


@router.patch("/{batch_id}/aggregate", response_model=BatchResponse, status_code=status.HTTP_202_ACCEPTED)
async def aggregate_batch(batch_id: UUID, request: AggregateBatchRequest, command: aggregate_batch) -> BatchResponse:
    """
    Агрегирует партию и все продукты в ней.
    """
    input_dto = aggregate_batch_request_to_input_dto(batch_id, request)
    batch_entity = await command.execute(input_dto)
    return domain_to_response(batch_entity)


@router.patch("/{batch_id}/aggregate_async", response_model=TaskStartedResponse, status_code=status.HTTP_202_ACCEPTED)
async def aggregate_batch_async(
    batch_id: UUID,
    request: AggregateBatchTaskRequest,
) -> TaskStartedResponse:
    """
    Запускает фоновую задачу для агрегации партии и продуктов в ней.

    Если указаны unique_codes, агрегируются только указанные продукты.
    Если unique_codes не указан, агрегируются все продукты партии.
    """
    aggregated_at_str = None
    if request.aggregated_at:
        aggregated_at_str = request.aggregated_at.isoformat()

    task = aggregate_batch_task.delay(
        batch_id=str(batch_id), unique_codes=request.unique_codes, aggregated_at=aggregated_at_str
    )

    return TaskStartedResponse(
        task_id=task.id,
        status=states.PENDING,
        message="Aggregation task started",
    )


@router.patch("/{batch_id}", response_model=BatchResponse)
async def update_batch(batch_id: UUID, request: UpdateBatchRequest, command: update_batch) -> BatchResponse:
    """
    Обновляет партию частично: только указанные поля.
    """
    input_dto = update_batch_request_to_input_dto(batch_id, request)
    batch_entity = await command.execute(input_dto)
    return domain_to_response(batch_entity)


@router.delete("/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_batch(batch_id: UUID, command: delete_batch) -> None:
    """
    Удаляет закрытую партию и все связанные продукты.

    ВАЖНО: Можно удалить только закрытую партию. Все продукты будут автоматически удалены.
    """
    await command.execute(batch_id)


@router.post(
    "/{batch_id}/reports/generate",
    response_model=GenerateReportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_report(
    batch_id: UUID,
    command: generate_report_command,
    format: ReportFormatEnum = Query(..., description="Формат отчета (pdf или excel)"),
    user_email: str | None = Query(None, description="Email адрес для отправки уведомления с отчетом"),
) -> GenerateReportResponse:
    """
    Генерирует отчет для партии
    """
    input_dto = GenerateReportInputDTO(batch_id=batch_id, format=format, user_email=user_email)
    result = await command.execute(input_dto)

    return GenerateReportResponse(report_path=result.report_path, download_url=result.download_url)


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
        raise ValueError(
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
    format: ExportImportFileFormatEnum,
    filters: BatchFiltersParams | None = None,
) -> TaskStartedResponse:
    """
    Экспортирует партии в файл.

    Экспорт выполняется асинхронно в фоновой задаче.
    """
    task = export_batches_task.delay(format=format, filters=filters)

    return TaskStartedResponse(
        task_id=task.id,
        status=states.PENDING,
        message="Export task started",
    )
