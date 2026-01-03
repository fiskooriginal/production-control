from src.application.common.cache.interface.protocol import CacheServiceProtocol
from src.application.common.cache.keys.batches import get_batches_list_pattern
from src.core.logging import get_logger
from src.domain.work_centers.events import WorkCenterDeletedEvent
from src.infrastructure.events.handlers.decorator import event_handler

logger = get_logger("handler.work_centers")


@event_handler(WorkCenterDeletedEvent)
class WorkCenterDeletedHandler:
    """Обработчик события удаления рабочего центра"""

    def __init__(self, cache_service: CacheServiceProtocol) -> None:
        self._cache_service = cache_service

    async def handle(self, event: WorkCenterDeletedEvent) -> None:
        """Обрабатывает событие удаления рабочего центра"""
        logger.info(f"Handling WorkCenterDeletedEvent: work_center_id={event.aggregate_id}")

        try:
            await self._cache_service.delete_pattern(get_batches_list_pattern())
            logger.info("Batches list cache deleted successfully")

            # ну и далее используется продюсер кафки/реббита для отправки сообщения в сервис уведомлений
            # о том, что партия закрыта и отчёт готов
        except Exception as e:
            logger.error(f"Failed to delete work center {event.aggregate_id}: {e}", exc_info=True)
