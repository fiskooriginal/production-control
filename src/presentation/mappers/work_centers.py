from uuid import UUID

from src.application.dtos.work_centers import CreateWorkCenterInputDTO, UpdateWorkCenterInputDTO
from src.domain.work_centers.entities import WorkCenterEntity
from src.presentation.api.schemas.work_centers import (
    CreateWorkCenterRequest,
    UpdateWorkCenterRequest,
    WorkCenterResponse,
)


def create_request_to_input_dto(request: CreateWorkCenterRequest) -> CreateWorkCenterInputDTO:
    """Конвертирует Pydantic CreateWorkCenterRequest в Application InputDTO"""
    return CreateWorkCenterInputDTO(
        identifier=request.identifier,
        name=request.name,
    )


def update_request_to_input_dto(work_center_id: str, request: UpdateWorkCenterRequest) -> UpdateWorkCenterInputDTO:
    """Конвертирует Pydantic UpdateWorkCenterRequest в Application InputDTO"""
    return UpdateWorkCenterInputDTO(
        work_center_id=UUID(work_center_id),
        identifier=request.identifier,
        name=request.name,
    )


def entity_to_response(entity: WorkCenterEntity) -> WorkCenterResponse:
    """Конвертирует Domain WorkCenterEntity в Pydantic Response"""
    return WorkCenterResponse(
        uuid=entity.uuid,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
        identifier=entity.identifier.value,
        name=entity.name.value,
    )
