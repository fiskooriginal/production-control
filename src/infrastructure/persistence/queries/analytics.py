from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.analytics.queries.dtos import DashboardStatisticsDTO
from src.application.analytics.queries.service import AnalyticsQueryServiceProtocol
from src.application.common.cache.interface.protocol import CacheServiceProtocol
from src.application.common.cache.keys.analytics import get_dashboard_stats_key
from src.core.logging import get_logger
from src.core.settings import AnalyticsSettings
from src.core.time import datetime_now
from src.infrastructure.common.exceptions import DatabaseException
from src.infrastructure.persistence.mappers.analytics import dto_to_json_bytes, json_bytes_to_dto
from src.infrastructure.persistence.models.batch import Batch
from src.infrastructure.persistence.models.product import Product

logger = get_logger("query.analytics")


class AnalyticsQueryService(AnalyticsQueryServiceProtocol):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_dashboard_statistics(self) -> DashboardStatisticsDTO:
        """Получает статистику дашборда"""
        try:
            total_batches_result = await self._session.execute(select(func.count()).select_from(Batch))
            total_batches = total_batches_result.scalar_one() or 0

            active_batches_result = await self._session.execute(
                select(func.count()).select_from(Batch).where(not Batch.is_closed)
            )
            active_batches = active_batches_result.scalar_one() or 0

            total_products_result = await self._session.execute(select(func.count()).select_from(Product))
            total_products = total_products_result.scalar_one() or 0

            aggregated_products_result = await self._session.execute(
                select(func.count()).select_from(Product).where(Product.is_aggregated)
            )
            aggregated_products = aggregated_products_result.scalar_one() or 0

            aggregation_rate = 0.0
            if total_products > 0:
                aggregation_rate = round((aggregated_products / total_products) * 100, 2)

            return DashboardStatisticsDTO(
                total_batches=total_batches,
                active_batches=active_batches,
                total_products=total_products,
                aggregated_products=aggregated_products,
                aggregation_rate=aggregation_rate,
            )
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении статистики дашборда: {e}") from e


class CachedAnalyticsQueryServiceProxy(AnalyticsQueryService):
    def __init__(self, session: AsyncSession, cache_service: CacheServiceProtocol):
        super().__init__(session)
        self._cache_service = cache_service

    async def get_dashboard_statistics(self) -> DashboardStatisticsDTO:
        """Получает статистику дашборда с кэшированием"""
        cache_key = get_dashboard_stats_key(self._cache_service.key_prefix)
        try:
            cached_data = await self._cache_service.get(cache_key)
            if cached_data:
                result = json_bytes_to_dto(cached_data)
                if result:
                    logger.info("Dashboard statistics found in cache")
                    return result
        except Exception as e:
            logger.warning(f"Failed to get dashboard statistics from cache: {e}")

        logger.info("Fetching dashboard statistics from database")
        query_result = await super().get_dashboard_statistics()

        try:
            query_result.cached_at = datetime_now()
            serialized = dto_to_json_bytes(query_result)

            analytics_settings = AnalyticsSettings()
            await self._cache_service.set(cache_key, serialized, ttl=analytics_settings.ttl_dashboard)
        except Exception as e:
            logger.warning(f"Failed to cache dashboard statistics: {e}")

        return query_result
