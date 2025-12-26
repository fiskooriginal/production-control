from uuid import UUID

from src.application.dtos.products import AggregateProductInputDTO
from src.domain.products.entities import ProductEntity
from src.presentation.api.schemas.products import AggregateProductRequest, ProductResponse


def aggregate_request_to_input_dto(product_id: str, request: AggregateProductRequest) -> AggregateProductInputDTO:
    """Конвертирует Pydantic AggregateProductRequest в Application InputDTO"""
    return AggregateProductInputDTO(
        product_id=UUID(product_id),
        aggregated_at=request.aggregated_at,
    )


def entity_to_response(entity: ProductEntity) -> ProductResponse:
    """Конвертирует Domain ProductEntity в Pydantic Response"""
    return ProductResponse(
        uuid=entity.uuid,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
        unique_code=entity.unique_code.value,
        batch_id=entity.batch_id,
        is_aggregated=entity.is_aggregated,
        aggregated_at=entity.aggregated_at,
    )
