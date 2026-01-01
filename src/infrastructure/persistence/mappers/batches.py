import json

from dataclasses import asdict
from datetime import date, datetime
from uuid import UUID

from dacite import Config, from_dict

from src.core.time import datetime_aware_to_naive, datetime_naive_to_aware
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
from src.domain.products.entities import ProductEntity
from src.infrastructure.common.exceptions import MappingException
from src.infrastructure.persistence.mappers.products import to_domain_entity as product_to_domain
from src.infrastructure.persistence.mappers.products import to_persistence_model as product_to_persistence_model
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


def dict_to_domain(domain_dict: dict) -> BatchEntity:
    """Конвертирует словарь в domain domain_entity BatchEntity (пропускается _domain_events)"""

    def str_to_uuid(value: str) -> UUID:
        return UUID(value)

    def str_to_datetime(value: str) -> datetime:
        dt = datetime.fromisoformat(value)
        return datetime_naive_to_aware(dt) if dt.tzinfo is None else dt

    def str_to_date(value: str) -> date:
        return date.fromisoformat(value)

    config = Config(
        forward_references={"ProductEntity": ProductEntity},
        type_hooks={UUID: str_to_uuid, datetime: str_to_datetime, date: str_to_date},
    )
    return from_dict(BatchEntity, domain_dict, config=config)


def domain_to_json_bytes(batch_entity: BatchEntity) -> bytes:
    """Сериализует BatchEntity в JSON bytes."""
    domain_dict = asdict(batch_entity)
    json_str = json.dumps(domain_dict, default=str)
    return json_str.encode("utf-8")


def json_bytes_to_domain(json_bytes: bytes) -> BatchEntity:
    """Десериализирует JSON bytes в BatchEntity"""
    json_str = json_bytes.decode("utf-8")
    domain_dict = json.loads(json_str)
    return dict_to_domain(domain_dict)
