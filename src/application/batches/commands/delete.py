from uuid import UUID

from src.application.common.cache.interface.protocol import CacheServiceProtocol
from src.application.common.cache.keys import get_batch_key, get_batches_list_pattern
from src.application.common.uow import UnitOfWorkProtocol
from src.core.logging import get_logger
from src.domain.batches.events import BatchDeletedEvent
from src.domain.common.exceptions import InvalidStateError

logger = get_logger("command.batches")


class DeleteBatchCommand:
    def __init__(self, uow: UnitOfWorkProtocol, cache_service: CacheServiceProtocol | None = None):
        self._uow = uow
        self._cache_service = cache_service

    async def execute(self, batch_id: UUID) -> None:
        """Удаляет закрытую партию с автоматическим сохранением доменных событий в outbox"""
        logger.info(f"Deleting batch: batch_id={batch_id}")
        try:
            async with self._uow:
                batch = await self._uow.batches.get_or_raise(batch_id)

                if not batch.is_closed:
                    raise InvalidStateError("Можно удалить только закрытую партию")

                batch.add_domain_event(BatchDeletedEvent(aggregate_id=batch.uuid, batch_number=batch.batch_number))
                await self._uow.batches.delete(batch_id)
                logger.info(f"Batch deleted successfully: batch_id={batch_id}")

            await self._invalidate_batch_cache(batch_id)
        except Exception as e:
            logger.exception(f"Failed to delete batch: {e}")
            raise

    async def _invalidate_batch_cache(self, batch_id: UUID) -> None:
        """Инвалидирует кэш для партии (best effort)."""
        if not self._cache_service or not self._cache_service.enabled:
            return
        try:
            await self._cache_service.delete(get_batch_key(batch_id, self._cache_service.key_prefix))
            await self._cache_service.delete_pattern(get_batches_list_pattern(self._cache_service.key_prefix))
        except Exception as e:
            logger.warning(f"Failed to invalidate cache for batch {batch_id}: {e}")
