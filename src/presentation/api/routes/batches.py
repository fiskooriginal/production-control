from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.application.batches.queries.use_cases import GetBatchQueryUseCase, ListBatchesQueryUseCase
from src.application.batches.use_cases import (
    AddProductToBatchUseCase,
    CloseBatchUseCase,
    CreateBatchUseCase,
    DeleteBatchUseCase,
    RemoveProductFromBatchUseCase,
    UpdateBatchUseCase,
)
from src.application.batches.use_cases.aggregate import AggregateBatchUseCase
from src.presentation.api.dependencies import (
    get_add_product_to_batch_use_case,
    get_aggregate_batch_use_case,
    get_batch_query_use_case,
    get_close_batch_use_case,
    get_create_batch_use_case,
    get_delete_batch_use_case,
    get_list_batches_query_use_case,
    get_remove_product_from_batch_use_case,
    get_update_batch_use_case,
)
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
    use_case: CreateBatchUseCase = Depends(get_create_batch_use_case),
) -> BatchResponse:
    """
    Создает новую партию.

    RESTful endpoint: POST /batches
    """
    input_dto = create_batch_request_to_input_dto(request)
    batch_entity = await use_case.execute(input_dto)
    return domain_to_response(batch_entity)


@router.patch("/{batch_id}/close", response_model=BatchResponse)
async def close_batch(
    batch_id: UUID,
    request: CloseBatchRequest,
    use_case: CloseBatchUseCase = Depends(get_close_batch_use_case),
) -> BatchResponse:
    """
    Закрывает партию.

    RESTful endpoint: PATCH /batches/{batch_id}/close
    """
    input_dto = close_batch_request_to_input_dto(batch_id, request)
    batch_entity = await use_case.execute(input_dto)
    return domain_to_response(batch_entity)


@router.post("/{batch_id}/products", response_model=BatchResponse)
async def add_product_to_batch(
    batch_id: UUID,
    request: AddProductToBatchRequest,
    use_case: AddProductToBatchUseCase = Depends(get_add_product_to_batch_use_case),
) -> BatchResponse:
    """
    Добавляет продукт в партию.

    RESTful endpoint: POST /batches/{batch_id}/products
    """
    batch_entity = await use_case.execute(batch_id, request.unique_code)
    return domain_to_response(batch_entity)


@router.delete("/{batch_id}/products/{product_id}", response_model=BatchResponse)
async def remove_product_from_batch(
    batch_id: UUID,
    product_id: UUID,
    use_case: RemoveProductFromBatchUseCase = Depends(get_remove_product_from_batch_use_case),
) -> BatchResponse:
    """
    Удаляет продукт из партии.

    RESTful endpoint: DELETE /batches/{batch_id}/products/{product_id}

    ВАЖНО: Продукт будет полностью удален из БД, так как batch_id NOT NULL.
    """
    batch_entity = await use_case.execute(batch_id, product_id)
    return domain_to_response(batch_entity)


@router.get("", response_model=ListBatchesResponse)
async def list_batches(
    filter_params: BatchFiltersParams = Depends(),
    pagination_params: PaginationParams = Depends(),
    sort_params: SortParams = Depends(),
    use_case: ListBatchesQueryUseCase = Depends(get_list_batches_query_use_case),
) -> ListBatchesResponse:
    """
    Получает список партий с фильтрацией, пагинацией и сортировкой.

    RESTful endpoint: GET /batches
    """
    query = build_list_batches_query(filter_params, pagination_params, sort_params)
    result = await use_case.execute(query)

    return ListBatchesResponse(
        items=[batch_read_dto_to_response(dto) for dto in result.items],
        total=result.total,
        limit=result.limit,
        offset=result.offset,
    )


@router.get("/{batch_id}", response_model=BatchResponse)
async def get_batch(
    batch_id: UUID,
    use_case: GetBatchQueryUseCase = Depends(get_batch_query_use_case),
) -> BatchResponse:
    """
    Получает партию по UUID.

    RESTful endpoint: GET /batches/{batch_id}
    """
    batch_dto = await use_case.execute(batch_id)
    return batch_read_dto_to_response(batch_dto)


@router.patch("/{batch_id}/aggregate", response_model=BatchResponse)
async def aggregate_batch(
    batch_id: UUID,
    request: AggregateBatchRequest,
    use_case: AggregateBatchUseCase = Depends(get_aggregate_batch_use_case),
) -> BatchResponse:
    """
    Агрегирует партию и все продукты в ней.

    RESTful endpoint: PATCH /batches/{batch_id}/aggregate
    """
    input_dto = aggregate_batch_request_to_input_dto(batch_id, request)
    batch_entity = await use_case.execute(input_dto)
    return domain_to_response(batch_entity)


@router.patch("/{batch_id}", response_model=BatchResponse)
async def update_batch(
    batch_id: UUID,
    request: UpdateBatchRequest,
    use_case: UpdateBatchUseCase = Depends(get_update_batch_use_case),
) -> BatchResponse:
    """
    Обновляет партию частично: только указанные поля.
    """
    input_dto = update_batch_request_to_input_dto(batch_id, request)
    batch_entity = await use_case.execute(input_dto)
    return domain_to_response(batch_entity)


@router.delete("/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_batch(
    batch_id: UUID,
    use_case: DeleteBatchUseCase = Depends(get_delete_batch_use_case),
) -> None:
    """
    Удаляет закрытую партию и все связанные продукты.

    RESTful endpoint: DELETE /batches/{batch_id}

    ВАЖНО: Можно удалить только закрытую партию. Все продукты будут автоматически удалены.
    """
    await use_case.execute(batch_id)
