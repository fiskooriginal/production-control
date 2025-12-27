from src.application.work_centers.queries import WorkCenterReadDTO
from src.infrastructure.persistence.models.work_center import WorkCenter


def work_center_model_to_read_dto(model: WorkCenter) -> WorkCenterReadDTO:
    """Преобразует модель SQLAlchemy в WorkCenterReadDTO"""
    return WorkCenterReadDTO(
        uuid=model.uuid,
        created_at=model.created_at,
        updated_at=model.updated_at,
        identifier=model.identifier,
        name=model.name,
    )
