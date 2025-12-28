from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.application.batches.commands import (
    AddProductToBatchCommand,
    AggregateBatchCommand,
    CloseBatchCommand,
    CreateBatchCommand,
    DeleteBatchCommand,
    RemoveProductFromBatchCommand,
    UpdateBatchCommand,
)
from src.application.batches.queries.handlers import GetBatchQueryHandler, ListBatchesQueryHandler
from src.presentation.api.dependencies import (
    get_add_product_to_batch_command,
    get_aggregate_batch_command,
    get_batch_query_handler,
    get_close_batch_command,
    get_create_batch_command,
    get_delete_batch_command,
    get_list_batches_query_handler,
    get_remove_product_from_batch_command,
    get_update_batch_command,
)
from src.presentation.api.schemas.background_tasks import TaskStartedResponse
from src.presentation.api.schemas.batches import (
    AddProductToBatchRequest,
    AggregateBatchRequest,
    BatchFiltersParams,
    BatchResponse,
    CloseBatchRequest,
    CreateBatchRequest,
    ListBatchesResponse,
    UpdateBatchRequest,
)
from src.presentation.api.schemas.query_params import PaginationParams, SortParams
from src.presentation.mappers.batches import (
    aggregate_batch_request_to_input_dto,
    close_batch_request_to_input_dto,
    create_batch_request_to_input_dto,
    domain_to_response,
    update_batch_request_to_input_dto,
)
from src.presentation.mappers.query_params import build_list_batches_query
from src.presentation.mappers.query_responses import batch_read_dto_to_response

router = APIRouter(prefix="/api/batches", tags=["batches"])


@router.post("", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
async def create_batch(
    request: CreateBatchRequest,
    command: CreateBatchCommand = Depends(get_create_batch_command),
) -> BatchResponse:
    """
    Создает новую партию.
    """
    input_dto = create_batch_request_to_input_dto(request)
    batch_entity = await command.execute(input_dto)
    return domain_to_response(batch_entity)


@router.patch("/{batch_id}/close", response_model=BatchResponse)
async def close_batch(
    batch_id: UUID,
    request: CloseBatchRequest,
    command: CloseBatchCommand = Depends(get_close_batch_command),
) -> BatchResponse:
    """
    Закрывает партию.
    """
    input_dto = close_batch_request_to_input_dto(batch_id, request)
    batch_entity = await command.execute(input_dto)
    return domain_to_response(batch_entity)


@router.post("/{batch_id}/products", response_model=BatchResponse)
async def add_product_to_batch(
    batch_id: UUID,
    request: AddProductToBatchRequest,
    command: AddProductToBatchCommand = Depends(get_add_product_to_batch_command),
) -> BatchResponse:
    """
    Добавляет продукт в партию.
    """
    batch_entity = await command.execute(batch_id, request.unique_code)
    return domain_to_response(batch_entity)


@router.delete("/{batch_id}/products/{product_id}", response_model=BatchResponse)
async def remove_product_from_batch(
    batch_id: UUID,
    product_id: UUID,
    command: RemoveProductFromBatchCommand = Depends(get_remove_product_from_batch_command),
) -> BatchResponse:
    """
    Удаляет продукт из партии.

    ВАЖНО: Продукт будет полностью удален из БД, так как batch_id NOT NULL.
    """
    batch_entity = await command.execute(batch_id, product_id)
    return domain_to_response(batch_entity)


@router.get("", response_model=ListBatchesResponse)
async def list_batches(
    filter_params: BatchFiltersParams = Depends(),
    pagination_params: PaginationParams = Depends(),
    sort_params: SortParams = Depends(),
    query_handler: ListBatchesQueryHandler = Depends(get_list_batches_query_handler),
) -> ListBatchesResponse:
    """
    Получает список партий с фильтрацией, пагинацией и сортировкой.
    """
    query = build_list_batches_query(filter_params, pagination_params, sort_params)
    result = await query_handler.execute(query)

    return ListBatchesResponse(
        items=[batch_read_dto_to_response(dto) for dto in result.items],
        total=result.total,
        limit=result.limit,
        offset=result.offset,
    )


@router.get("/{batch_id}", response_model=BatchResponse)
async def get_batch(
    batch_id: UUID,
    query_handler: GetBatchQueryHandler = Depends(get_batch_query_handler),
) -> BatchResponse:
    """
    Получает партию по UUID.
    """
    batch_dto = await query_handler.execute(batch_id)
    return batch_read_dto_to_response(batch_dto)


@router.patch("/{batch_id}/aggregate", response_model=TaskStartedResponse, status_code=status.HTTP_202_ACCEPTED)
async def aggregate_batch(
    batch_id: UUID,
    request: AggregateBatchRequest,
    command: AggregateBatchCommand = Depends(get_aggregate_batch_command),
) -> TaskStartedResponse:
    """
    Агрегирует партию и все продукты в ней.
    """
    input_dto = aggregate_batch_request_to_input_dto(batch_id, request)
    batch_entity = await command.execute(input_dto)
    return domain_to_response(batch_entity)


@router.patch("/{batch_id}", response_model=BatchResponse)
async def update_batch(
    batch_id: UUID,
    request: UpdateBatchRequest,
    command: UpdateBatchCommand = Depends(get_update_batch_command),
) -> BatchResponse:
    """
    Обновляет партию частично: только указанные поля.
    """
    input_dto = update_batch_request_to_input_dto(batch_id, request)
    batch_entity = await command.execute(input_dto)
    return domain_to_response(batch_entity)


@router.delete("/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_batch(
    batch_id: UUID,
    command: DeleteBatchCommand = Depends(get_delete_batch_command),
) -> None:
    """
    Удаляет закрытую партию и все связанные продукты.

    ВАЖНО: Можно удалить только закрытую партию. Все продукты будут автоматически удалены.
    """
    await command.execute(batch_id)
