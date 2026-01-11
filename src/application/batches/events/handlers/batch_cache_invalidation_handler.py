from src.application.common.cache.interfaces import CacheServiceProtocol
from src.application.common.cache.keys.batches import get_batch_key, get_batches_list_pattern
from src.core.logging import get_logger
from src.domain.common.events import DomainEvent

logger = get_logger("batches.events.handlers.batch_report_generation_handler")


class BatchCacheInvalidationHandler:
    """Обработчик событий Batch для инвалидации кэша"""

    def __init__(self, cache_service: CacheServiceProtocol | None) -> None:
        self._cache_service = cache_service

    async def handle(self, event: DomainEvent) -> None:
        """Обрабатывает событие Batch, инвалидируя кэш для партии"""
        logger.info(f"Handling cache invalidation for batch event: event_type={type(event).__name__}")

        if not self._cache_service or not self._cache_service.enabled:
            logger.debug("Cache service is not available or disabled, skipping cache invalidation for batches")
            return

        if hasattr(event, "batch_id"):
            batch_id = event.batch_id
            await self._cache_service.delete(get_batch_key(batch_id, self._cache_service.key_prefix))
            logger.info(f"Cache invalidated successfully for GET batch: batch_id={batch_id}")
        try:
            await self._cache_service.delete_pattern(get_batches_list_pattern(self._cache_service.key_prefix))
            logger.info("Cache invalidated successfully for LIST batch")
        except Exception as e:
            logger.warning(f"Failed to invalidate cache for batches: {e}", exc_info=True)
