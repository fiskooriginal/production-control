from src.domain.work_centers.entities import WorkCenterEntity
from src.domain.work_centers.value_objects import WorkCenterIdentifier, WorkCenterName
from src.infrastructure.exceptions import MappingException
from src.infrastructure.persistence.mappers.shared import datetime_aware_to_naive, datetime_naive_to_aware
from src.infrastructure.persistence.models.work_center import WorkCenter


def to_domain_entity(work_center_model: WorkCenter) -> WorkCenterEntity:
    """Конвертирует persistence модель WorkCenter в domain domain_entity WorkCenterEntity"""
    try:
        return WorkCenterEntity(
            uuid=work_center_model.uuid,
            created_at=datetime_naive_to_aware(work_center_model.created_at),
            updated_at=datetime_naive_to_aware(work_center_model.updated_at),
            identifier=WorkCenterIdentifier(work_center_model.identifier),
            name=WorkCenterName(work_center_model.name),
        )
    except Exception as e:
        raise MappingException(f"Ошибка маппинга persistence -> domain для WorkCenter: {e}") from e


def to_persistence_model(work_center_entity: WorkCenterEntity, existing_model: WorkCenter | None = None) -> WorkCenter:
    """Конвертирует domain domain_entity WorkCenterEntity в persistence модель WorkCenter"""
    try:
        author = existing_model.author if existing_model else work_center_entity.uuid
        return WorkCenter(
            uuid=work_center_entity.uuid,
            created_at=datetime_aware_to_naive(work_center_entity.created_at),
            updated_at=datetime_aware_to_naive(work_center_entity.updated_at),
            identifier=work_center_entity.identifier.value,
            name=work_center_entity.name.value,
            author=author,
        )
    except Exception as e:
        raise MappingException(f"Ошибка маппинга domain -> persistence для WorkCenter: {e}") from e
