from src.application.dtos.batches import CloseBatchInputDTO, CreateBatchInputDTO
from src.domain.batches.entities import BatchEntity
from src.presentation.api.schemas.batches import (
    BatchResponse,
    CloseBatchRequest,
    CreateBatchRequest,
    ShiftTimeRangeSchema,
)
from src.presentation.mappers.products import entity_to_response as product_to_response


def create_batch_request_to_input_dto(request: CreateBatchRequest) -> CreateBatchInputDTO:
    """Конвертирует Pydantic CreateBatchRequest в Application InputDTO"""
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


def close_batch_request_to_input_dto(batch_id: str, request: CloseBatchRequest) -> CloseBatchInputDTO:
    """Конвертирует Pydantic CloseBatchRequest в Application InputDTO"""
    from uuid import UUID

    return CloseBatchInputDTO(
        batch_id=UUID(batch_id),
        closed_at=request.closed_at,
    )


def domain_to_response(entity: BatchEntity) -> BatchResponse:
    """Конвертирует Domain BatchEntity в Pydantic Response"""
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
