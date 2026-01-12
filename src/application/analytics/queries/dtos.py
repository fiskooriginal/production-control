from dataclasses import dataclass
from datetime import datetime


@dataclass
class DashboardStatisticsDTO:
    """DTO для статистики дашборда"""

    total_batches: int
    active_batches: int
    total_products: int
    aggregated_products: int
    aggregation_rate: float
    cached_at: datetime | None = None
