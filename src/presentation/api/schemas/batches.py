from datetime import date, datetime
from typing import Annotated
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field

from src.presentation.api.schemas.base import TimestampSchema, UUIDSchema
from src.presentation.api.schemas.products import ProductResponse


class ShiftTimeRangeSchema(BaseModel):
    """Вложенная схема для времени смены"""

    start: datetime = Field(..., description="Начало смены")
    end: datetime = Field(..., description="Конец смены")


class AggregateBatchRequest(BaseModel):
    """Request schema для агрегации партии"""

    aggregated_at: datetime | None = Field(None, description="Время агрегации (если не указано, используется текущее)")
    unique_codes: list[str] | None = Field(
        None,
        description="Список уникальных кодов продуктов для агрегации. Если не указан, агрегируются все продукты партии.",
    )


class CreateBatchRequest(BaseModel):
    """Request schema для создания партии"""

    task_description: str = Field(..., min_length=1, description="Описание задания")
    shift: str = Field(..., min_length=1, description="Смена")
    team: str = Field(..., min_length=1, description="Бригада")

    batch_number: int = Field(..., gt=0, description="Номер партии")
    batch_date: date = Field(..., description="Дата партии")

    nomenclature: str = Field(..., min_length=1, description="Номенклатура")
    ekn_code: str = Field(..., min_length=1, description="ЕКН код")

    shift_start: datetime = Field(..., description="Начало смены")
    shift_end: datetime = Field(..., description="Конец смены")

    work_center_id: UUID = Field(..., description="ID рабочего центра")


class UpdateBatchRequest(BaseModel):
    """Request schema для обновления партии"""

    task_description: str | None = Field(None, min_length=1, description="Описание задания")
    shift: str | None = Field(None, min_length=1, description="Смена")
    team: str | None = Field(None, min_length=1, description="Бригада")

    batch_number: int | None = Field(None, gt=0, description="Номер партии")
    batch_date: date | None = Field(None, description="Дата партии")

    nomenclature: str | None = Field(None, min_length=1, description="Номенклатура")
    ekn_code: str | None = Field(None, min_length=1, description="ЕКН код")

    shift_start: datetime | None = Field(None, description="Начало смены")
    shift_end: datetime | None = Field(None, description="Конец смены")

    work_center_id: UUID | None = Field(None, description="ID рабочего центра")

    is_closed: bool | None = Field(None, description="Статус партии")


class CloseBatchRequest(BaseModel):
    """Request schema для закрытия партии"""

    closed_at: datetime | None = Field(None, description="Время закрытия (если не указано, используется текущее)")


class AddProductToBatchRequest(BaseModel):
    """Request schema для добавления продукта в партию"""

    unique_code: str = Field(..., min_length=1, description="Уникальный код продукта")


class BatchResponse(UUIDSchema, TimestampSchema, BaseModel):
    """Response schema для партии"""

    is_closed: bool = Field(..., description="Статус партии")
    closed_at: datetime | None = Field(None, description="Время закрытия партии")
    task_description: str = Field(..., description="Описание задания")
    shift: str = Field(..., description="Смена")
    team: str = Field(..., description="Бригада")
    batch_number: int = Field(..., description="Номер партии")
    batch_date: date = Field(..., description="Дата партии")
    nomenclature: str = Field(..., description="Номенклатура")
    ekn_code: str = Field(..., description="ЕКН код")
    shift_time_range: ShiftTimeRangeSchema = Field(..., description="Временной диапазон смены")
    work_center_id: UUID = Field(..., description="ID рабочего центра")
    products: list[ProductResponse] = Field(..., description="Продукты в партии")

    class Config:
        from_attributes = True


class BatchFiltersParams(BaseModel):
    """Query параметры для фильтрации партий"""

    is_closed: Annotated[bool | None, Query(description="Фильтр по статусу закрытия")] = None
    batch_number: Annotated[int | None, Query(gt=0, description="Фильтр по номеру партии")] = None
    batch_date: Annotated[str | None, Query(description="Фильтр по дате партии (YYYY-MM-DD)")] = None
    work_center_id: Annotated[str | None, Query(description="Фильтр по ID рабочего центра")] = None
    shift: Annotated[str | None, Query(description="Фильтр по смене")] = None


class ListBatchesResponse(BaseModel):
    """Response schema для списка партий"""

    items: list[BatchResponse] = Field(..., description="Список партий")
    total: int = Field(..., description="Общее количество партий")
    limit: int | None = Field(None, description="Лимит элементов на странице")
    offset: int | None = Field(None, description="Смещение от начала")

    class Config:
        from_attributes = True
