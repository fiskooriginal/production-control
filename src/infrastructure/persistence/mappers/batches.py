from src.domain.batches.entities import BatchEntity
from src.domain.batches.value_objects import (
    BatchNumber,
    EknCode,
    Nomenclature,
    Shift,
    ShiftTimeRange,
    TaskDescription,
    Team,
)
from src.infrastructure.exceptions import MappingException
from src.infrastructure.persistence.mappers.products import to_domain_entity as product_to_domain
from src.infrastructure.persistence.mappers.products import to_persistence_model as product_to_persistence_model
from src.infrastructure.persistence.mappers.shared import datetime_aware_to_naive, datetime_naive_to_aware
from src.infrastructure.persistence.models.batch import Batch


def to_domain_entity(batch_model: Batch) -> BatchEntity:
    """Конвертирует persistence модель Batch в domain domain_entity BatchEntity"""
    try:
        return BatchEntity(
            uuid=batch_model.uuid,
            created_at=datetime_naive_to_aware(batch_model.created_at),
            updated_at=datetime_naive_to_aware(batch_model.updated_at),
            is_closed=batch_model.is_closed,
            closed_at=datetime_naive_to_aware(batch_model.closed_at),
            task_description=TaskDescription(batch_model.task_description),
            shift=Shift(batch_model.shift),
            team=Team(batch_model.team),
            batch_number=BatchNumber(batch_model.batch_number),
            batch_date=batch_model.batch_date,
            nomenclature=Nomenclature(batch_model.nomenclature),
            ekn_code=EknCode(batch_model.ekn_code),
            shift_time_range=ShiftTimeRange(
                start=datetime_naive_to_aware(batch_model.shift_start_time),
                end=datetime_naive_to_aware(batch_model.shift_end_time),
            ),
            products=[product_to_domain(p) for p in batch_model.products],
            work_center_id=batch_model.work_center_id,
        )
    except Exception as e:
        raise MappingException(f"Ошибка маппинга persistence -> domain для Batch: {e}") from e


def to_persistence_model(batch_entity: BatchEntity) -> Batch:
    """Конвертирует domain domain_entity BatchEntity в persistence модель Batch"""
    try:
        return Batch(
            uuid=batch_entity.uuid,
            created_at=datetime_aware_to_naive(batch_entity.created_at),
            updated_at=datetime_aware_to_naive(batch_entity.updated_at),
            is_closed=batch_entity.is_closed,
            closed_at=datetime_aware_to_naive(batch_entity.closed_at),
            task_description=batch_entity.task_description.value,
            shift=batch_entity.shift.value,
            team=batch_entity.team.value,
            batch_number=batch_entity.batch_number.value,
            batch_date=batch_entity.batch_date,
            nomenclature=batch_entity.nomenclature.value,
            ekn_code=batch_entity.ekn_code.value,
            shift_start_time=datetime_aware_to_naive(batch_entity.shift_time_range.start),
            shift_end_time=datetime_aware_to_naive(batch_entity.shift_time_range.end),
            work_center_id=batch_entity.work_center_id,
            products=[product_to_persistence_model(p) for p in batch_entity.products],
        )
    except Exception as e:
        raise MappingException(f"Ошибка маппинга domain -> persistence для Batch: {e}") from e
