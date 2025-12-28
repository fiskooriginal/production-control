from uuid import UUID

from fastapi import APIRouter, Depends

from src.application.products.commands import AggregateProductCommand
from src.application.products.queries.handlers import GetProductQueryHandler, ListProductsQueryHandler
from src.presentation.api.dependencies import (
    get_aggregate_product_command,
    get_list_products_query_handler,
    get_product_query_handler,
)
from src.presentation.api.schemas.products import AggregateProductRequest, ListProductsResponse, ProductResponse
from src.presentation.api.schemas.query_params import PaginationParams, SortParams
from src.presentation.mappers.products import aggregate_request_to_input_dto, entity_to_response
from src.presentation.mappers.query_params import build_list_products_query
from src.presentation.mappers.query_responses import product_read_dto_to_response

router = APIRouter(prefix="/api/products", tags=["products"])


@router.patch("/{product_id}/aggregate", response_model=ProductResponse)
async def aggregate_product(
    product_id: UUID,
    request: AggregateProductRequest,
    command: AggregateProductCommand = Depends(get_aggregate_product_command),
) -> ProductResponse:
    """
    Агрегирует продукт.
    """
    input_dto = aggregate_request_to_input_dto(product_id, request)
    product_entity = await command.execute(input_dto)
    return entity_to_response(product_entity)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    query_handler: GetProductQueryHandler = Depends(get_product_query_handler),
) -> ProductResponse:
    """
    Получает продукт по UUID.
    """
    product_dto = await query_handler.execute(product_id)
    return product_read_dto_to_response(product_dto)


@router.get("", response_model=ListProductsResponse)
async def list_products(
    pagination_params: PaginationParams = Depends(),
    sort_params: SortParams = Depends(),
    query_handler: ListProductsQueryHandler = Depends(get_list_products_query_handler),
) -> ListProductsResponse:
    """
    Получает список продуктов с пагинацией и сортировкой.
    """
    query = build_list_products_query(pagination_params, sort_params)
    result = await query_handler.execute(query)
    return ListProductsResponse(
        items=[product_read_dto_to_response(dto) for dto in result.items],
        total=result.total,
        limit=result.limit,
        offset=result.offset,
    )
