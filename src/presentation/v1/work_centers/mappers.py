from uuid import UUID

from src.application.work_centers.dtos.create import CreateWorkCenterInputDTO
from src.application.work_centers.dtos.update import UpdateWorkCenterInputDTO
from src.application.work_centers.queries.filters import WorkCenterReadFilters
from src.application.work_centers.queries.queries import ListWorkCentersQuery
from src.application.work_centers.queries.sort import WorkCenterSortField, WorkCenterSortSpec
from src.domain.work_centers import WorkCenterEntity
from src.presentation.exceptions import SerializationException
from src.presentation.v1.common.mappers import pagination_params_to_spec
from src.presentation.v1.common.schemas import PaginationParams, SortParams
from src.presentation.v1.work_centers.schemas import (
    CreateWorkCenterRequest,
    UpdateWorkCenterRequest,
    WorkCenterFiltersParams,
    WorkCenterResponse,
)


def create_request_to_input_dto(request: CreateWorkCenterRequest) -> CreateWorkCenterInputDTO:
    """Конвертирует Pydantic CreateWorkCenterRequest в Application InputDTO"""
    try:
        return CreateWorkCenterInputDTO(
            identifier=request.identifier,
            name=request.name,
        )
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации CreateWorkCenterRequest: {e}") from e


def update_request_to_input_dto(work_center_id: UUID, request: UpdateWorkCenterRequest) -> UpdateWorkCenterInputDTO:
    """Конвертирует Pydantic UpdateWorkCenterRequest в Application InputDTO"""
    try:
        return UpdateWorkCenterInputDTO(work_center_id=work_center_id, identifier=request.identifier, name=request.name)
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации UpdateWorkCenterRequest: {e}") from e


def domain_to_response(entity: WorkCenterEntity) -> WorkCenterResponse:
    """Конвертирует Domain WorkCenterEntity в Pydantic Response"""
    try:
        return WorkCenterResponse(
            uuid=entity.uuid,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            identifier=entity.identifier.value,
            name=entity.name.value,
        )
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации WorkCenterEntity в response: {e}") from e


def work_center_filters_params_to_query(params: WorkCenterFiltersParams) -> WorkCenterReadFilters | None:
    """Конвертирует WorkCenterFiltersParams в WorkCenterReadFilters"""
    try:
        if params.identifier:
            return WorkCenterReadFilters(identifier=params.identifier)
        return None
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации WorkCenterFiltersParams: {e}") from e


def sort_params_to_work_center_sort_spec(params: SortParams) -> WorkCenterSortSpec | None:
    """Конвертирует SortParams в WorkCenterSortSpec"""
    try:
        if params.sort_field and params.sort_direction:
            try:
                sort_field = WorkCenterSortField(params.sort_field)
            except ValueError as ve:
                raise SerializationException(
                    f"Недопустимое поле сортировки для work_centers: {params.sort_field}. "
                    f"Допустимые значения: {', '.join([f.value for f in WorkCenterSortField])}"
                ) from ve
            return WorkCenterSortSpec(field=sort_field, direction=params.sort_direction)
        return None
    except SerializationException:
        raise
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации SortParams: {e}") from e


def build_list_work_centers_query(
    filter_params: WorkCenterFiltersParams,
    pagination_params: PaginationParams,
    sort_params: SortParams,
) -> ListWorkCentersQuery:
    """Создает ListWorkCentersQuery из параметров запроса"""
    filters = work_center_filters_params_to_query(filter_params)
    pagination = pagination_params_to_spec(pagination_params)
    sort = sort_params_to_work_center_sort_spec(sort_params)

    return ListWorkCentersQuery(filters=filters, pagination=pagination, sort=sort)
