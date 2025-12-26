from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.application.use_cases.batches import (
    AddProductToBatchUseCase,
    CloseBatchUseCase,
    CreateBatchUseCase,
    GetBatchUseCase,
    ListBatchesUseCase,
    RemoveProductFromBatchUseCase,
)
from src.presentation.api.dependencies import (
    get_add_product_to_batch_use_case,
    get_batch_use_case,
    get_close_batch_use_case,
    get_create_batch_use_case,
    get_list_batches_use_case,
    get_remove_product_from_batch_use_case,
)
from src.presentation.api.schemas.batches import (
    AddProductToBatchRequest,
    BatchFiltersParams,
    BatchResponse,
    CloseBatchRequest,
    CreateBatchRequest,
    ListBatchesResponse,
)
from src.presentation.api.schemas.query_params import PaginationParams, SortParams
from src.presentation.mappers.batches import (
    close_batch_request_to_input_dto,
    create_batch_request_to_input_dto,
    domain_to_response,
)
from src.presentation.mappers.query_params import (
    batch_filters_params_to_dto,
    pagination_params_to_spec,
    sort_params_to_spec,
)

router = APIRouter(prefix="/batches", tags=["batches"])


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
    use_case: ListBatchesUseCase = Depends(get_list_batches_use_case),
) -> ListBatchesResponse:
    """
    Получает список партий с фильтрацией, пагинацией и сортировкой.

    RESTful endpoint: GET /batches
    """
    filters = batch_filters_params_to_dto(filter_params)
    pagination = pagination_params_to_spec(pagination_params)
    sort = sort_params_to_spec(sort_params)

    result = await use_case.execute(filters=filters, pagination=pagination, sort=sort)

    return ListBatchesResponse(
        items=[domain_to_response(entity) for entity in result.items],
        total=result.total,
        limit=result.limit,
        offset=result.offset,
    )


@router.get("/{batch_id}", response_model=BatchResponse)
async def get_batch(
    batch_id: UUID,
    use_case: GetBatchUseCase = Depends(get_batch_use_case),
) -> BatchResponse:
    """
    Получает партию по UUID.

    RESTful endpoint: GET /batches/{batch_id}
    """
    batch_entity = await use_case.execute(batch_id)
    return domain_to_response(batch_entity)
