from typing import Protocol

from src.application.analytics.queries.dtos import DashboardStatisticsDTO


class AnalyticsQueryServiceProtocol(Protocol):
    async def get_dashboard_statistics(self) -> DashboardStatisticsDTO:
        """Получает статистику дашборда"""
        ...
