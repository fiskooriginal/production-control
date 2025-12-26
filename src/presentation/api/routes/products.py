from uuid import UUID

from fastapi import APIRouter, Depends

from src.application.use_cases.products import AggregateProductUseCase
from src.presentation.api.dependencies import get_aggregate_product_use_case
from src.presentation.api.schemas.products import AggregateProductRequest, ProductResponse
from src.presentation.mappers.products import aggregate_request_to_input_dto, entity_to_response

router = APIRouter(prefix="/products", tags=["products"])


@router.patch("/{product_id}/aggregate", response_model=ProductResponse)
async def aggregate_product(
    product_id: UUID,
    request: AggregateProductRequest,
    use_case: AggregateProductUseCase = Depends(get_aggregate_product_use_case),
) -> ProductResponse:
    """
    Агрегирует продукт.

    RESTful endpoint: PATCH /products/{product_id}/aggregate
    """
    input_dto = aggregate_request_to_input_dto(product_id, request)
    product_entity = await use_case.execute(input_dto)
    return entity_to_response(product_entity)
