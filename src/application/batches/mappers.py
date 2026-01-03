import json

from dataclasses import asdict, fields
from datetime import date, datetime
from typing import Any
from uuid import UUID

from src.application.batches.dtos.create import CreateBatchInputDTO
from src.application.batches.dtos.raw_data import BatchRawDataDTO, ProductRawDataDTO
from src.application.batches.dtos.update import UpdateBatchInputDTO
from src.domain.batches import BatchEntity
from src.domain.batches.value_objects import (
    BatchImportRow,
    BatchNumber,
    EknCode,
    Nomenclature,
    Shift,
    ShiftTimeRange,
    TaskDescription,
    Team,
)
from src.domain.products import ProductEntity
from src.domain.work_centers import WorkCenterEntity


def product_entity_to_raw_data_dto(product: ProductEntity) -> ProductRawDataDTO:
    """Маппер из ProductEntity в ProductRawDataDTO"""
    return ProductRawDataDTO(
        uuid=product.uuid,
        created_at=product.created_at,
        updated_at=product.updated_at,
        unique_code=product.unique_code.value,
        batch_id=product.batch_id,
        is_aggregated=product.is_aggregated,
        aggregated_at=product.aggregated_at,
    )


def product_raw_data_dto_to_entity(dto: ProductRawDataDTO) -> ProductEntity:
    """Маппер из ProductRawDataDTO в ProductEntity (используется только для валидации структуры)"""
    from src.domain.products.value_objects import ProductCode

    return ProductEntity(
        uuid=dto.uuid,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
        unique_code=ProductCode(dto.unique_code),
        batch_id=dto.batch_id,
        is_aggregated=dto.is_aggregated,
        aggregated_at=dto.aggregated_at,
    )


def create_input_dto_to_entity(dto: CreateBatchInputDTO) -> BatchEntity:
    """Маппер из CreateBatchInputDTO в BatchEntity"""
    return BatchEntity(
        task_description=TaskDescription(dto.task_description),
        shift=Shift(dto.shift),
        team=Team(dto.team),
        batch_number=BatchNumber(dto.batch_number),
        batch_date=dto.batch_date,
        nomenclature=Nomenclature(dto.nomenclature),
        ekn_code=EknCode(dto.ekn_code),
        shift_time_range=ShiftTimeRange(start=dto.shift_start, end=dto.shift_end),
        products=[],
        work_center_id=dto.work_center_id,
    )


def import_row_to_create_dto(import_row: BatchImportRow, work_center_id: UUID) -> CreateBatchInputDTO:
    """Маппер из BatchImportRow (Value Object) в CreateBatchInputDTO"""
    return CreateBatchInputDTO(
        task_description=str(import_row.task_description),
        shift=str(import_row.shift),
        team=str(import_row.team),
        batch_number=import_row.batch_number.value,
        batch_date=import_row.batch_date,
        nomenclature=str(import_row.nomenclature),
        ekn_code=str(import_row.ekn_code),
        shift_start=import_row.shift_time_range.start,
        shift_end=import_row.shift_time_range.end,
        work_center_id=work_center_id,
    )


def import_row_to_update_dto(
    import_row: BatchImportRow, existing_batch_uuid: UUID, work_center_id: UUID
) -> UpdateBatchInputDTO:
    """Маппер из BatchImportRow (Value Object) в UpdateBatchInputDTO"""
    return UpdateBatchInputDTO(
        batch_id=existing_batch_uuid,
        task_description=str(import_row.task_description),
        shift=str(import_row.shift),
        team=str(import_row.team),
        batch_number=import_row.batch_number.value,
        batch_date=import_row.batch_date,
        nomenclature=str(import_row.nomenclature),
        ekn_code=str(import_row.ekn_code),
        shift_start=import_row.shift_time_range.start,
        shift_end=import_row.shift_time_range.end,
        work_center_id=work_center_id,
        is_closed=import_row.is_closed,
    )


def raw_data_dto_to_row(dto: BatchRawDataDTO) -> list:
    """
    Преобразует DTO в строку данных для экспорта.

    Args:
        dto: DTO объект

    Returns:
        Список значений в том же порядке, что и заголовки
    """

    def get_field_value(dto: Any, field_name: str) -> Any:
        """Получает значение поля из DTO с правильной форматизацией."""
        value = getattr(dto, field_name)

        if value is None:
            return ""

        if isinstance(value, UUID):
            return str(value)

        if isinstance(value, (date, datetime)):
            return value.isoformat()

        if isinstance(value, bool):
            return value

        if isinstance(value, str) and field_name == "products":
            return value

        return value

    row = []
    for field in fields(BatchRawDataDTO):
        value = get_field_value(dto, field.name)
        row.append(value)

    return row


def dict_to_raw_data_dto(row_data: dict[str, Any]) -> BatchRawDataDTO:
    """
    Маппер из словаря (результат парсинга файла) в BatchRawDataDTO.

    Обрабатывает поля shift_time_range.start и shift_time_range.end из файла,
    преобразуя их в shift_start и shift_end в DTO.
    Преобразует строковые значения в соответствующие типы (UUID, date, datetime).
    """

    def _parse_uuid(value: Any) -> UUID | None:
        if value is None or value == "":
            return None
        if isinstance(value, UUID):
            return value
        if isinstance(value, str):
            return UUID(value)
        raise ValueError(f"Не удалось преобразовать {value} в UUID")

    def _parse_date(value: Any) -> date:
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            return date.fromisoformat(value)
        raise ValueError(f"Не удалось преобразовать {value} в date")

    def _parse_datetime(value: Any) -> datetime | None:
        if value is None or value == "":
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        raise ValueError(f"Не удалось преобразовать {value} в datetime")

    shift_start = row_data.get("shift_time_range.start") or row_data.get("shift_start")
    shift_end = row_data.get("shift_time_range.end") or row_data.get("shift_end")

    work_center_identifier = row_data.get("work_center_identifier")
    if not work_center_identifier or work_center_identifier == "":
        raise ValueError("work_center_identifier обязателен и не может быть пустым")

    shift_start_parsed = _parse_datetime(shift_start)
    if shift_start_parsed is None:
        raise ValueError("shift_start обязателен и не может быть пустым")

    shift_end_parsed = _parse_datetime(shift_end)
    if shift_end_parsed is None:
        raise ValueError("shift_end обязателен и не может быть пустым")

    products_json = row_data.get("products", "[]")
    if not isinstance(products_json, str):
        products_json = json.dumps(products_json, default=str)

    return BatchRawDataDTO(
        batch_number=int(row_data["batch_number"]),
        batch_date=_parse_date(row_data["batch_date"]),
        nomenclature=str(row_data["nomenclature"]),
        ekn_code=str(row_data["ekn_code"]),
        shift=str(row_data["shift"]),
        team=str(row_data["team"]),
        task_description=str(row_data["task_description"]),
        shift_start=shift_start_parsed,
        shift_end=shift_end_parsed,
        work_center_identifier=str(work_center_identifier),
        uuid=_parse_uuid(row_data.get("uuid")),
        created_at=_parse_datetime(row_data.get("created_at")),
        updated_at=_parse_datetime(row_data.get("updated_at")),
        is_closed=bool(row_data["is_closed"]) if row_data.get("is_closed") is not None else None,
        closed_at=_parse_datetime(row_data.get("closed_at")),
        products=products_json,
    )


def raw_data_dto_to_entity(dto: BatchRawDataDTO, work_center_id: UUID) -> BatchEntity:
    """
    Маппер из BatchRawDataDTO в BatchEntity.

    Преобразует DTO с данными из файла экспорта/импорта в доменную сущность.
    Если uuid, created_at, updated_at не указаны, используются дефолтные значения из BaseEntity.

    Args:
        dto: DTO с данными партии
        work_center_id: UUID рабочего центра (получается из найденного/созданного рабочего центра)
    """
    entity_kwargs = {
        "task_description": TaskDescription(dto.task_description),
        "shift": Shift(dto.shift),
        "team": Team(dto.team),
        "batch_number": BatchNumber(dto.batch_number),
        "batch_date": dto.batch_date,
        "nomenclature": Nomenclature(dto.nomenclature),
        "ekn_code": EknCode(dto.ekn_code),
        "shift_time_range": ShiftTimeRange(start=dto.shift_start, end=dto.shift_end),
        "products": [],
        "work_center_id": work_center_id,
        "is_closed": dto.is_closed if dto.is_closed is not None else False,
        "closed_at": dto.closed_at,
    }

    if dto.uuid is not None:
        entity_kwargs["uuid"] = dto.uuid

    if dto.created_at is not None:
        entity_kwargs["created_at"] = dto.created_at

    if dto.updated_at is not None:
        entity_kwargs["updated_at"] = dto.updated_at

    return BatchEntity(**entity_kwargs)


def entity_to_raw_data_dto(batch_entity: BatchEntity, work_center_entity: WorkCenterEntity) -> BatchRawDataDTO:
    """
    Маппер из BatchEntity в BatchRawDataDTO.

    Преобразует доменную сущность в DTO для экспорта/импорта.

    Args:
        entity: Доменная сущность партии
        work_center_identifier: Идентификатор рабочего центра (опционально, должен быть загружен отдельно)
    """
    products_json = "[]"
    if batch_entity.products:
        products_dto = [product_entity_to_raw_data_dto(product) for product in batch_entity.products]
        products_dict = [asdict(product) for product in products_dto]
        products_json = json.dumps(products_dict, default=str)

    return BatchRawDataDTO(
        uuid=batch_entity.uuid,
        created_at=batch_entity.created_at,
        updated_at=batch_entity.updated_at,
        batch_number=batch_entity.batch_number.value,
        batch_date=batch_entity.batch_date,
        nomenclature=str(batch_entity.nomenclature),
        ekn_code=str(batch_entity.ekn_code),
        shift=str(batch_entity.shift),
        team=str(batch_entity.team),
        task_description=str(batch_entity.task_description),
        shift_start=batch_entity.shift_time_range.start,
        shift_end=batch_entity.shift_time_range.end,
        is_closed=batch_entity.is_closed,
        closed_at=batch_entity.closed_at,
        work_center_identifier=str(work_center_entity.identifier),
        work_center_name=str(work_center_entity.name),
        products=products_json,
    )
