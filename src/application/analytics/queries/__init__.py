from src.application.analytics.queries.dtos import DashboardStatisticsDTO
from src.application.analytics.queries.handlers import GetDashboardStatisticsQueryHandler
from src.application.analytics.queries.service import AnalyticsQueryServiceProtocol

__all__ = [
    "AnalyticsQueryServiceProtocol",
    "DashboardStatisticsDTO",
    "GetDashboardStatisticsQueryHandler",
]
