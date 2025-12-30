from uuid import UUID

from src.application.batches.reports.adapters import ReportStorageAdapter
from src.application.batches.reports.dtos import ReportFormatEnum
from src.application.batches.reports.ports import ReportGeneratorProtocol
from src.application.batches.reports.services import ReportDataService
from src.application.common.exceptions import ApplicationException
from src.core.logging import get_logger

logger = get_logger("service.reports")


class ReportGenerationService:
    """Сервис для генерации отчетов"""

    def __init__(
        self,
        report_data_service: ReportDataService,
        pdf_generator: ReportGeneratorProtocol,
        excel_generator: ReportGeneratorProtocol,
        report_storage: ReportStorageAdapter,
    ) -> None:
        self._report_data_service = report_data_service
        self._pdf_generator = pdf_generator
        self._excel_generator = excel_generator
        self._report_storage = report_storage

    async def _get_generator_cls(self, format: ReportFormatEnum) -> ReportGeneratorProtocol:
        generator_cls = {
            ReportFormatEnum.PDF: self._pdf_generator,
            ReportFormatEnum.EXCEL: self._excel_generator,
        }
        return generator_cls[format]

    async def generate_report(self, batch_id: UUID, report_format: ReportFormatEnum):
        """Генерирует отчёт для партии"""
        logger.info(f"Начата генерация отчёта для партии: batch_id={batch_id}")
        try:
            batch_data = await self._report_data_service.get_batch_report_data(batch_id)

            generator_cls = await self._get_generator_cls(report_format)
            content = await generator_cls.generate(batch_data)

            report_path = await self._report_storage.save_report(batch_id, content, report_format)
            logger.info(f"Отчёт успешно сгенерирован: batch_id={batch_id}, path={report_path}")
            return report_path
        except ApplicationException:
            raise
        except Exception as e:
            logger.exception(f"Ошибка при генерации отчтёта для партии {batch_id}: {e}")
            raise ApplicationException(f"Ошибка при генерации отчета: {e}") from e
