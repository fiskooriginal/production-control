from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.presentation.v1.batches.di.commands import close_batch, create_batch, delete_batch, update_batch
from src.presentation.v1.batches.di.queries import get_batch, list_batches
from src.presentation.v1.batches.mappers import (
    build_list_batches_query,
    close_batch_request_to_input_dto,
    create_batch_request_to_input_dto,
    domain_to_response,
    update_batch_request_to_input_dto,
)
from src.presentation.v1.batches.schemas.filters import BatchFiltersParams
from src.presentation.v1.batches.schemas.requests import CloseBatchRequest, CreateBatchRequest, UpdateBatchRequest
from src.presentation.v1.batches.schemas.responses import BatchResponse, ListBatchesResponse
from src.presentation.v1.common.schemas import PaginationParams, SortParams

router = APIRouter()


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
