from src.application.common.cache.keys.analytics import get_dashboard_stats_key
from src.core.logging import get_logger
from src.core.settings import CacheSettings
from src.infrastructure.background_tasks.app import celery_app, get_session_factory, run_async_task
from src.infrastructure.common.cache.redis import close_cache, init_cache
from src.infrastructure.persistence.queries.analytics import CachedAnalyticsQueryServiceProxy

logger = get_logger("celery.tasks.update_dashboard_stats")


@celery_app.task(name="tasks.update_dashboard_stats")
def update_dashboard_stats() -> dict:
    """
    Обновляет статистику дашборда и сохраняет её в кэш.

    Returns:
        {
            "success": True,
            "cached": True
        }
    """
    return run_async_task(_update_dashboard_stats_async())


async def _update_dashboard_stats_async() -> dict:
    """Асинхронная часть задачи обновления статистики дашборда"""
    session_factory = get_session_factory()
    cache_settings = CacheSettings()

    if not cache_settings.enabled:
        logger.warning("Cache is disabled, statistics not cached")
        return {"success": False, "cached": False}

    cache_service, pool = await init_cache(cache_settings, raise_error=True)
    cache_key = get_dashboard_stats_key(cache_service.key_prefix)
    try:
        async with session_factory() as session:
            logger.info("Starting dashboard statistics update")

            await cache_service.delete(cache_key)
            query_service = CachedAnalyticsQueryServiceProxy(session, cache_service)
            statistics = await query_service.get_dashboard_statistics()

            logger.info(
                f"Dashboard statistics cached: total_batches={statistics.total_batches}, "
                f"active_batches={statistics.active_batches}, total_products={statistics.total_products}"
            )

            return {
                "success": True,
                "cached": cache_settings.enabled,
            }
    except Exception as e:
        logger.exception(f"Failed to update dashboard statistics: {e}")
        raise
    finally:
        await close_cache(pool)
