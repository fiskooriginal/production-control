from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.presentation.v1.common.schemas import TimestampSchema, UUIDSchema
from src.presentation.v1.products.schemas import ProductResponse


class ShiftTimeRangeSchema(BaseModel):
    """Вложенная схема для времени смены"""

    start: datetime = Field(..., description="Начало смены")
    end: datetime = Field(..., description="Конец смены")


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


class ListBatchesResponse(BaseModel):
    """Response schema для списка партий"""

    items: list[BatchResponse] = Field(..., description="Список партий")
    total: int = Field(..., description="Общее количество партий")
    limit: int | None = Field(None, description="Лимит элементов на странице")
    offset: int | None = Field(None, description="Смещение от начала")

    class Config:
        from_attributes = True


class GenerateReportResponse(BaseModel):
    """Ответ с информацией о сгенерированном отчете."""

    report_path: str
    download_url: str | None = None
