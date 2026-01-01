from src.application.analytics.queries.dtos import DashboardStatisticsDTO
from src.presentation.api.schemas.analytics import DashboardStatisticsResponse


def dashboard_statistics_dto_to_response(dto: DashboardStatisticsDTO) -> DashboardStatisticsResponse:
    return DashboardStatisticsResponse(
        total_batches=dto.total_batches,
        active_batches=dto.active_batches,
        total_products=dto.total_products,
        aggregated_products=dto.aggregated_products,
        aggregation_rate=dto.aggregation_rate,
        cached_at=dto.cached_at,
    )
