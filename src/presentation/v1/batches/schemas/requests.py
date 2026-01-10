from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AggregateBatchRequest(BaseModel):
    """Request schema для агрегации партии"""

    aggregated_at: datetime | None = Field(None, description="Время агрегации (если не указано, используется текущее)")


class AggregateBatchTaskRequest(BaseModel):
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
