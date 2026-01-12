from datetime import date
from uuid import UUID

from src.application.batches.dtos.aggregate import AggregateBatchInputDTO
from src.application.batches.dtos.close import CloseBatchInputDTO
from src.application.batches.dtos.create import CreateBatchInputDTO
from src.application.batches.dtos.update import UpdateBatchInputDTO
from src.application.batches.queries.filters import BatchReadFilters
from src.application.batches.queries.queries import ListBatchesQuery
from src.application.batches.queries.sort import BatchSortField, BatchSortSpec
from src.domain.batches import BatchEntity
from src.presentation.exceptions import SerializationException
from src.presentation.v1.batches.schemas.filters import BatchFiltersParams
from src.presentation.v1.batches.schemas.requests import (
    AggregateBatchRequest,
    CloseBatchRequest,
    CreateBatchRequest,
    UpdateBatchRequest,
)
from src.presentation.v1.batches.schemas.responses import BatchResponse, ShiftTimeRangeSchema
from src.presentation.v1.common.mappers import pagination_params_to_spec
from src.presentation.v1.common.schemas import PaginationParams, SortParams
from src.presentation.v1.products.mappers import domain_to_response as product_to_response


def create_batch_request_to_input_dto(request: CreateBatchRequest) -> CreateBatchInputDTO:
    """Конвертирует Pydantic CreateBatchRequest в Application InputDTO"""
    try:
        return CreateBatchInputDTO(
            task_description=request.task_description,
            shift=request.shift,
            team=request.team,
            batch_number=request.batch_number,
            batch_date=request.batch_date,
            nomenclature=request.nomenclature,
            ekn_code=request.ekn_code,
            shift_start=request.shift_start,
            shift_end=request.shift_end,
            work_center_id=request.work_center_id,
        )
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации CreateBatchRequest: {e}") from e


def close_batch_request_to_input_dto(batch_id: UUID, request: CloseBatchRequest) -> CloseBatchInputDTO:
    """Конвертирует Pydantic CloseBatchRequest в Application InputDTO"""
    try:
        return CloseBatchInputDTO(batch_id=batch_id, closed_at=request.closed_at)
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации CloseBatchRequest: {e}") from e


def domain_to_response(entity: BatchEntity) -> BatchResponse:
    """Конвертирует Domain BatchEntity в Pydantic Response"""
    try:
        return BatchResponse(
            uuid=entity.uuid,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_closed=entity.is_closed,
            closed_at=entity.closed_at,
            task_description=entity.task_description.value,
            shift=entity.shift.value,
            team=entity.team.value,
            batch_number=entity.batch_number.value,
            batch_date=entity.batch_date,
            nomenclature=entity.nomenclature.value,
            ekn_code=entity.ekn_code.value,
            shift_time_range=ShiftTimeRangeSchema(
                start=entity.shift_time_range.start,
                end=entity.shift_time_range.end,
            ),
            work_center_id=entity.work_center_id,
            products=[product_to_response(product) for product in entity.products],
        )
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации BatchEntity в response: {e}") from e


def aggregate_batch_request_to_input_dto(batch_id: UUID, request: AggregateBatchRequest) -> AggregateBatchInputDTO:
    """Конвертирует Pydantic AggregateProductRequest в Application InputDTO"""
    try:
        return AggregateBatchInputDTO(batch_id=batch_id, aggregated_at=request.aggregated_at)
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации AggregateProductRequest: {e}") from e


def update_batch_request_to_input_dto(batch_id: UUID, request: UpdateBatchRequest) -> UpdateBatchInputDTO:
    """Конвертирует Pydantic UpdateBatchRequest в Application InputDTO"""
    try:
        return UpdateBatchInputDTO(
            batch_id=batch_id,
            task_description=request.task_description,
            shift=request.shift,
            team=request.team,
            batch_number=request.batch_number,
            batch_date=request.batch_date,
            nomenclature=request.nomenclature,
            ekn_code=request.ekn_code,
            shift_start=request.shift_start,
            shift_end=request.shift_end,
            work_center_id=request.work_center_id,
            is_closed=request.is_closed,
        )
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации UpdateBatchRequest: {e}") from e


def batch_filters_params_to_query(params: BatchFiltersParams) -> BatchReadFilters:
    """Конвертирует BatchFiltersParams в BatchReadFilters"""
    try:
        filter_dict = {}

        if params.is_closed is not None:
            filter_dict["is_closed"] = params.is_closed

        if params.batch_number is not None:
            filter_dict["batch_number"] = params.batch_number

        if params.batch_date:
            filter_dict["batch_date"] = date.fromisoformat(params.batch_date)

        if params.batch_date_from:
            filter_dict["batch_date_from"] = date.fromisoformat(params.batch_date_from)

        if params.batch_date_to:
            filter_dict["batch_date_to"] = date.fromisoformat(params.batch_date_to)

        if params.work_center_id:
            filter_dict["work_center_id"] = UUID(params.work_center_id)

        if params.shift:
            filter_dict["shift"] = params.shift

        return BatchReadFilters(**filter_dict)
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации BatchFiltersParams: {e}") from e


def sort_params_to_batch_sort_spec(params: SortParams) -> BatchSortSpec | None:
    """Конвертирует SortParams в BatchSortSpec"""
    try:
        if params.sort_field and params.sort_direction:
            try:
                sort_field = BatchSortField(params.sort_field)
            except ValueError as ve:
                raise SerializationException(
                    f"Недопустимое поле сортировки для batches: {params.sort_field}. "
                    f"Допустимые значения: {', '.join([f.value for f in BatchSortField])}"
                ) from ve
            return BatchSortSpec(field=sort_field, direction=params.sort_direction)
        return None
    except SerializationException:
        raise
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации SortParams: {e}") from e


def build_list_batches_query(
    filter_params: BatchFiltersParams,
    pagination_params: PaginationParams,
    sort_params: SortParams,
) -> ListBatchesQuery:
    """Создает ListBatchesQuery из параметров запроса"""
    filters = batch_filters_params_to_query(filter_params)
    pagination = pagination_params_to_spec(pagination_params)
    sort = sort_params_to_batch_sort_spec(sort_params)

    return ListBatchesQuery(filters=filters, pagination=pagination, sort=sort)
