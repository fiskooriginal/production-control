from uuid import UUID

from src.application.batches.dtos import (
    AggregateBatchInputDTO,
    CloseBatchInputDTO,
    CreateBatchInputDTO,
    UpdateBatchInputDTO,
)
from src.domain.batches.entities import BatchEntity
from src.presentation.api.schemas.batches import (
    AggregateBatchRequest,
    BatchResponse,
    CloseBatchRequest,
    CreateBatchRequest,
    ShiftTimeRangeSchema,
    UpdateBatchRequest,
)
from src.presentation.exceptions import SerializationException
from src.presentation.mappers.products import entity_to_response as product_to_response


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
