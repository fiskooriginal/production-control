from fastapi import APIRouter

from src.presentation.v1.analytics.di import get_dashboard_statistics
from src.presentation.v1.analytics.mappers import dashboard_statistics_dto_to_response
from src.presentation.v1.analytics.schemas import DashboardStatisticsResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardStatisticsResponse)
async def get_dashboard(query_handler: get_dashboard_statistics) -> DashboardStatisticsResponse:
    """
    Получает статистику дашборда из кэша.

    Статистика обновляется Celery Beat каждые 5 минут.
    """

    statistics = await query_handler.execute()
    return dashboard_statistics_dto_to_response(statistics)
