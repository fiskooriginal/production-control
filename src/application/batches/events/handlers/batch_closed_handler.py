from src.application.batches.reports.dtos import ReportFormatEnum
from src.application.batches.reports.services.report_generation_service import ReportGenerationService
from src.core.logging import get_logger
from src.domain.batches.events import BatchClosedEvent
from src.infrastructure.events.handlers.decorator import event_handler

logger = get_logger("handler.batches.closed")


@event_handler(BatchClosedEvent)
class BatchClosedHandler:
    """Обработчик события закрытия партии для автоматической генерации PDF отчета"""

    def __init__(self, report_generation_service: ReportGenerationService) -> None:
        self._report_generation_service = report_generation_service

    async def handle(self, event: BatchClosedEvent) -> None:
        """Обрабатывает событие закрытия партии, генерируя PDF отчет"""
        logger.info(f"Handling BatchClosedEvent: batch_id={event.aggregate_id}")

        try:
            await self._report_generation_service.generate_report(event.aggregate_id, ReportFormatEnum.PDF)
            logger.info(f"Report generated successfully for batch: batch_id={event.aggregate_id}")

            # ну и далее используется продюсер кафки/реббита для отправки сообщения в сервис уведомлений
            # о том, что партия закрыта и отчёт готов
        except Exception as e:
            logger.error(f"Failed to generate report for batch {event.aggregate_id}: {e}", exc_info=True)
