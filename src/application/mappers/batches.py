from collections.abc import Callable
from typing import TYPE_CHECKING

from src.application.mappers.products import to_domain_entity as product_to_domain
from src.data.persistence.models.batch import Batch
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

if TYPE_CHECKING:
    from src.domain.products.entities import ProductEntity


def to_domain_entity(batch_model: Batch, product_mapper: Callable | None = None) -> BatchEntity:
    """Конвертирует persistence модель Batch в domain entity BatchEntity"""
    mapper = product_mapper or product_to_domain
    products: list[ProductEntity] = []
    if batch_model.products:
        products = [mapper(p) for p in batch_model.products]
    return BatchEntity(
        uuid=batch_model.uuid,
        created_at=batch_model.created_at,
        updated_at=batch_model.updated_at,
        is_closed=batch_model.is_closed,
        closed_at=batch_model.closed_at,
        task_description=TaskDescription(batch_model.task_description),
        shift=Shift(batch_model.shift),
        team=Team(batch_model.team),
        batch_number=BatchNumber(batch_model.batch_number),
        batch_date=batch_model.batch_date,
        nomenclature=Nomenclature(batch_model.nomenclature),
        ekn_code=EknCode(batch_model.ekn_code),
        shift_time_range=ShiftTimeRange(start=batch_model.shift_start_time, end=batch_model.shift_end_time),
        products=products,
        work_center_id=batch_model.work_center_id,
    )


def to_persistence_model(batch_entity: BatchEntity) -> Batch:
    """Конвертирует domain entity BatchEntity в persistence модель Batch"""
    return Batch(
        uuid=batch_entity.uuid,
        created_at=batch_entity.created_at,
        updated_at=batch_entity.updated_at,
        is_closed=batch_entity.is_closed,
        closed_at=batch_entity.closed_at,
        task_description=batch_entity.task_description.value,
        shift=batch_entity.shift.value,
        team=batch_entity.team.value,
        batch_number=batch_entity.batch_number.value,
        batch_date=batch_entity.batch_date,
        nomenclature=batch_entity.nomenclature.value,
        ekn_code=batch_entity.ekn_code.value,
        shift_start_time=batch_entity.shift_time_range.start,
        shift_end_time=batch_entity.shift_time_range.end,
        work_center_id=batch_entity.work_center_id,
    )
