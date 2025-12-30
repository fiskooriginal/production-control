from uuid import UUID

from src.application.batches.queries import BatchQueryServiceProtocol
from src.application.batches.reports.dtos import BatchReportOutputDTO
from src.application.batches.reports.statistics import calculate_statistics
from src.application.common.exceptions import ApplicationException
from src.application.work_centers.queries import WorkCenterQueryServiceProtocol
from src.core.logging import get_logger

logger = get_logger("service.reports")


class ReportDataService:
    """Сервис для получения данных для генерации отчетов"""

    def __init__(
        self,
        batch_query_service: BatchQueryServiceProtocol,
        work_center_query_service: WorkCenterQueryServiceProtocol | None = None,
    ) -> None:
        self._batch_query_service = batch_query_service
        self._work_center_query_service = work_center_query_service

    async def get_batch_report_data(self, batch_id: UUID) -> BatchReportOutputDTO:
        """Получает данные для генерации отчета по партии"""
        logger.info(f"Getting report data for batch: batch_id={batch_id}")

        try:
            batch = await self._batch_query_service.get(batch_id)

            if batch is None:
                raise ApplicationException(f"Партия с ID {batch_id} не найдена")

            statistics = calculate_statistics(batch)

            work_center_name = None
            if self._work_center_query_service is not None:
                work_center = await self._work_center_query_service.get(batch.work_center_id)
                if work_center is not None:
                    work_center_name = work_center.name

            return BatchReportOutputDTO(batch=batch, statistics=statistics, work_center_name=work_center_name)
        except ApplicationException:
            raise
        except Exception as e:
            logger.exception(f"Failed to get report data for batch {batch_id}: {e}")
            raise ApplicationException(f"Ошибка при получении данных для отчета: {e}") from e
