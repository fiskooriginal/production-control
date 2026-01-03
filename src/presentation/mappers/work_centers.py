from uuid import UUID

from src.application.work_centers.dtos.create import CreateWorkCenterInputDTO
from src.application.work_centers.dtos.update import UpdateWorkCenterInputDTO
from src.domain.work_centers import WorkCenterEntity
from src.presentation.api.schemas.work_centers import (
    CreateWorkCenterRequest,
    UpdateWorkCenterRequest,
    WorkCenterResponse,
)
from src.presentation.exceptions import SerializationException


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
