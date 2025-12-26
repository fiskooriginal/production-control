from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.presentation.api.schemas.base import TimestampSchema, UUIDSchema


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
