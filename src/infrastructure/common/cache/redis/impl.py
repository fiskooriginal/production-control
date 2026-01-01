from redis.asyncio import Redis

from src.application.common.cache.interface.protocol import CacheServiceProtocol
from src.core.logging import get_logger
from src.core.settings import CacheSettings

logger = get_logger("cache")


class RedisCacheService(CacheServiceProtocol):
    """Сервис кэширования на основе Redis с обработкой ошибок best effort."""

    def __init__(self, redis_client: Redis, redis_settings: CacheSettings, raise_error: bool = False):
        self._client = redis_client
        self._settings = redis_settings
        self._raise_errors = raise_error

    @property
    def enabled(self) -> bool:
        """Проверяет, включен ли кэш."""
        return self._settings.enabled

    @property
    def ttl_get(self) -> int:
        """TTL для отдельной сущности в секундах."""
        return self._settings.ttl_get

    @property
    def ttl_list(self) -> int:
        """TTL для списков в секундах."""
        return self._settings.ttl_list

    @property
    def key_prefix(self) -> str:
        """Префикс для ключей кэша."""
        return self._settings.key_prefix

    async def get(self, key: str) -> bytes | None:
        """Получает значение по ключу. Возвращает None при ошибке."""
        try:
            value = await self._client.get(key)
            return value
        except Exception as e:
            logger.warning(f"Failed to get cache key {key}: {e}")
            if self._raise_errors:
                raise

    async def set(self, key: str, value: bytes, ttl: int | None = None) -> None:
        """Устанавливает значение с опциональным TTL. Молча игнорирует ошибки."""
        try:
            await self._client.set(key, value, ex=ttl)
        except Exception as e:
            logger.warning(f"Failed to set cache key {key}: {e}")
            if self._raise_errors:
                raise

    async def delete(self, key: str) -> None:
        """Удаляет значение по ключу. Молча игнорирует ошибки."""
        try:
            await self._client.delete(key)
        except Exception as e:
            logger.warning(f"Failed to delete cache key {key}: {e}")
            if self._raise_errors:
                raise

    async def delete_pattern(self, pattern: str) -> None:
        """Удаляет все ключи по паттерну. Молча игнорирует ошибки."""
        try:
            cursor = 0
            while True:
                cursor, keys = await self._client.scan(cursor, match=pattern, count=100)
                if keys:
                    await self._client.delete(*keys)
                if cursor == 0:
                    break
        except Exception as e:
            logger.warning(f"Failed to delete cache pattern {pattern}: {e}")
            if self._raise_errors:
                raise
