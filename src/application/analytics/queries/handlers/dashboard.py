from src.application.analytics.queries.dtos import DashboardStatisticsDTO
from src.application.analytics.queries.service import AnalyticsQueryServiceProtocol
from src.core.logging import get_logger

logger = get_logger("query.handler.analytics")


class GetDashboardStatisticsQueryHandler:
    def __init__(self, query_service: AnalyticsQueryServiceProtocol):
        self._query_service = query_service

    async def execute(self) -> DashboardStatisticsDTO:
        """Получает статистику дашборда"""
        logger.debug("Getting dashboard statistics")
        try:
            result = await self._query_service.get_dashboard_statistics()
            logger.debug(f"Dashboard statistics retrieved: total_batches={result.total_batches}")
            return result
        except Exception as e:
            logger.exception(f"Failed to get dashboard statistics: {e}")
            raise
