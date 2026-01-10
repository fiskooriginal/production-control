from typing import Annotated

from fastapi import Depends

from src.application.analytics.queries.handlers.dashboard import GetDashboardStatisticsQueryHandler
from src.infrastructure.persistence.queries.analytics import AnalyticsQueryService, CachedAnalyticsQueryServiceProxy
from src.presentation.v1.common.di import async_session, cache


async def get_analytics_query_service(session: async_session, cache_service: cache) -> AnalyticsQueryService:
    """Dependency для AnalyticsQueryService"""
    if cache_service and cache_service.enabled:
        return CachedAnalyticsQueryServiceProxy(session, cache_service)
    return AnalyticsQueryService(session)


analytics_query = Annotated[AnalyticsQueryService, Depends(get_analytics_query_service)]


async def get_dashboard_statistics_query_handler(query_service: analytics_query) -> GetDashboardStatisticsQueryHandler:
    """Dependency для GetDashboardStatisticsQueryHandler"""
    return GetDashboardStatisticsQueryHandler(query_service)


get_dashboard_statistics = Annotated[
    GetDashboardStatisticsQueryHandler, Depends(get_dashboard_statistics_query_handler)
]
