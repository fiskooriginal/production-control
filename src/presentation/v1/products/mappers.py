from uuid import UUID

from src.application.products.dtos import AggregateProductInputDTO
from src.application.products.queries.queries import ListProductsQuery
from src.application.products.queries.sort import ProductSortField, ProductSortSpec
from src.domain.products import ProductEntity
from src.presentation.exceptions import SerializationException
from src.presentation.v1.common.mappers import pagination_params_to_spec
from src.presentation.v1.common.schemas import PaginationParams, SortParams
from src.presentation.v1.products.schemas import AggregateProductRequest, ProductResponse


def aggregate_request_to_input_dto(product_id: UUID, request: AggregateProductRequest) -> AggregateProductInputDTO:
    """Конвертирует Pydantic AggregateProductRequest в Application InputDTO"""
    try:
        return AggregateProductInputDTO(product_id=product_id, aggregated_at=request.aggregated_at)
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации AggregateProductRequest: {e}") from e


def domain_to_response(entity: ProductEntity) -> ProductResponse:
    """Конвертирует Domain ProductEntity в Pydantic Response"""
    try:
        return ProductResponse(
            uuid=entity.uuid,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            unique_code=entity.unique_code.value,
            batch_id=entity.batch_id,
            is_aggregated=entity.is_aggregated,
            aggregated_at=entity.aggregated_at,
        )
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации ProductEntity в response: {e}") from e


def sort_params_to_product_sort_spec(params: SortParams) -> ProductSortSpec | None:
    """Конвертирует SortParams в ProductSortSpec"""
    try:
        if params.sort_field and params.sort_direction:
            try:
                sort_field = ProductSortField(params.sort_field)
            except ValueError as ve:
                raise SerializationException(
                    f"Недопустимое поле сортировки для products: {params.sort_field}. "
                    f"Допустимые значения: {', '.join([f.value for f in ProductSortField])}"
                ) from ve
            return ProductSortSpec(field=sort_field, direction=params.sort_direction)
        return None
    except SerializationException:
        raise
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации SortParams: {e}") from e


def build_list_products_query(
    pagination_params: PaginationParams,
    sort_params: SortParams,
) -> ListProductsQuery:
    """Создает ListProductsQuery из параметров запроса"""
    pagination = pagination_params_to_spec(pagination_params)
    sort = sort_params_to_product_sort_spec(sort_params)

    return ListProductsQuery(pagination=pagination, sort=sort)
