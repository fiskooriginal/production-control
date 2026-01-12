from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.presentation.v1.common.schemas import TimestampSchema, UUIDSchema


class AggregateProductRequest(BaseModel):
    """Request schema для агрегации продукта"""

    aggregated_at: datetime | None = Field(None, description="Время агрегации (если не указано, используется текущее)")


class ProductResponse(UUIDSchema, TimestampSchema, BaseModel):
    """Response schema для продукта"""

    unique_code: str = Field(..., description="Уникальный код продукта")
    batch_id: UUID = Field(..., description="ID партии")
    is_aggregated: bool = Field(..., description="Статус агрегации")
    aggregated_at: datetime | None = Field(None, description="Время агрегации")

    class Config:
        from_attributes = True


class ListProductsResponse(BaseModel):
    """Response schema для списка продуктов"""

    items: list[ProductResponse] = Field(..., description="Список продуктов")
    total: int = Field(..., description="Общее количество продуктов")
    limit: int | None = Field(None, description="Лимит элементов на странице")
    offset: int | None = Field(None, description="Смещение от начала")

    class Config:
        from_attributes = True
