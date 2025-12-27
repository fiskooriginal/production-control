from dataclasses import replace

from src.application.work_centers.dtos import CreateWorkCenterInputDTO, UpdateWorkCenterInputDTO
from src.domain.work_centers.entities import WorkCenterEntity
from src.domain.work_centers.value_objects import WorkCenterIdentifier, WorkCenterName


def create_input_dto_to_entity(dto: CreateWorkCenterInputDTO) -> WorkCenterEntity:
    """Маппер из CreateWorkCenterInputDTO в WorkCenterEntity"""
    return WorkCenterEntity(
        identifier=WorkCenterIdentifier(dto.identifier),
        name=WorkCenterName(dto.name),
    )


def update_dto_to_entity(entity: WorkCenterEntity, dto: UpdateWorkCenterInputDTO) -> WorkCenterEntity:
    """Маппер для обновления WorkCenterEntity из UpdateWorkCenterInputDTO"""
    updates = {}
    if dto.identifier is not None:
        updates["identifier"] = WorkCenterIdentifier(dto.identifier)
    if dto.name is not None:
        updates["name"] = WorkCenterName(dto.name)

    return replace(entity, **updates)
