from src.domain.work_centers.entities import WorkCenterEntity
from src.domain.work_centers.value_objects import WorkCenterIdentifier, WorkCenterName
from src.infrastructure.persistence.models.work_center import WorkCenter


def to_domain_entity(work_center_model: WorkCenter) -> WorkCenterEntity:
    """Конвертирует persistence модель WorkCenter в domain entity WorkCenterEntity"""
    return WorkCenterEntity(
        uuid=work_center_model.uuid,
        created_at=work_center_model.created_at,
        updated_at=work_center_model.updated_at,
        identifier=WorkCenterIdentifier(work_center_model.identifier),
        name=WorkCenterName(work_center_model.name),
    )


def to_persistence_model(work_center_entity: WorkCenterEntity, existing_model: WorkCenter | None = None) -> WorkCenter:
    """Конвертирует domain entity WorkCenterEntity в persistence модель WorkCenter"""
    author = existing_model.author if existing_model else work_center_entity.uuid
    return WorkCenter(
        uuid=work_center_entity.uuid,
        created_at=work_center_entity.created_at,
        updated_at=work_center_entity.updated_at,
        identifier=work_center_entity.identifier.value,
        name=work_center_entity.name.value,
        author=author,
    )
