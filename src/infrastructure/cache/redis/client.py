from redis.asyncio import ConnectionPool, Redis

from src.core.logging import get_logger
from src.core.settings import CacheSettings, RedisSettings
from src.infrastructure.cache.redis.impl import RedisCacheService

logger = get_logger("cache.client")


async def init_cache(cache_settings: CacheSettings) -> tuple[RedisCacheService | None, ConnectionPool | None]:
    """
    Инициализирует Redis кэш сервис и connection pool.
    Возвращает (cache_service, redis_pool) или (None, None) если кэш отключен или произошла ошибка.
    """
    if not cache_settings.enabled:
        logger.info("Cache is disabled")
        return None, None

    try:
        redis_settings = RedisSettings()
        redis_pool = ConnectionPool.from_url(
            redis_settings.get_url(),
            max_connections=10,
            decode_responses=False,
        )
        redis_client = Redis(connection_pool=redis_pool)
        cache_service = RedisCacheService(redis_client, cache_settings)
        logger.info("Redis cache initialized successfully")
        return cache_service, redis_pool
    except Exception as e:
        logger.warning(f"Failed to initialize Redis cache: {e}. Continuing without cache.")
        return None, None


async def close_cache(redis_pool: ConnectionPool | None) -> None:
    """Закрывает Redis connection pool."""
    if redis_pool:
        try:
            await redis_pool.aclose()
            logger.info("Redis connection pool closed")
        except Exception as e:
            logger.warning(f"Failed to close Redis connection pool: {e}")
