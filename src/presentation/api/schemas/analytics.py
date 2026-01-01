from datetime import datetime

from pydantic import BaseModel, Field


class DashboardStatisticsResponse(BaseModel):
    """Response schema для статистики дашборда"""

    total_batches: int = Field(..., description="Общее количество партий")
    active_batches: int = Field(..., description="Количество активных партий (не закрытых)")
    total_products: int = Field(..., description="Общее количество продуктов")
    aggregated_products: int = Field(..., description="Количество агрегированных продуктов")
    aggregation_rate: float = Field(..., description="Процент агрегации")
    cached_at: datetime | None = Field(None, description="Время кэширования статистики")
