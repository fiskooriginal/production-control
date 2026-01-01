from fastapi import APIRouter

from src.presentation.api.schemas.analytics import DashboardStatisticsResponse
from src.presentation.di.analytics import get_dashboard_statistics
from src.presentation.mappers.analytics import dashboard_statistics_dto_to_response

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardStatisticsResponse)
async def get_dashboard(query_handler: get_dashboard_statistics) -> DashboardStatisticsResponse:
    """
    Получает статистику дашборда из кэша.

    Статистика обновляется Celery Beat каждые 5 минут.
    """

    statistics = await query_handler.execute()
    return dashboard_statistics_dto_to_response(statistics)
