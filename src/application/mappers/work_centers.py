from dataclasses import replace

from src.application.dtos.work_centers import CreateWorkCenterInputDTO, UpdateWorkCenterInputDTO
from src.domain.work_centers.entities import WorkCenterEntity
from src.domain.work_centers.value_objects import WorkCenterIdentifier, WorkCenterName


def input_dto_to_entity(dto: CreateWorkCenterInputDTO) -> WorkCenterEntity:
    """
    Конвертирует CreateWorkCenterInputDTO в доменную сущность WorkCenterEntity.
    Только конвертация InputDTO → Domain, без бизнес-логики.
    """
    return WorkCenterEntity(
        identifier=WorkCenterIdentifier(dto.identifier),
        name=WorkCenterName(dto.name),
    )


def update_dto_to_entity(entity: WorkCenterEntity, dto: UpdateWorkCenterInputDTO) -> WorkCenterEntity:
    """
    Обновляет доменную сущность WorkCenterEntity из UpdateWorkCenterInputDTO.
    """
    updates = {}
    if dto.identifier is not None:
        updates["identifier"] = WorkCenterIdentifier(dto.identifier)
    if dto.name is not None:
        updates["name"] = WorkCenterName(dto.name)

    return replace(entity, **updates)
