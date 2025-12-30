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

    async def generate_pdf_report(self, batch_id: UUID) -> str:
        """Генерирует PDF отчет для партии"""
        logger.info(f"Generating PDF report for batch: batch_id={batch_id}")

        try:
            batch_data = await self._report_data_service.get_batch_report_data(batch_id)

            pdf_content = await self._pdf_generator.generate(batch_data)

            report_path = await self._report_storage.save_report(batch_id, pdf_content, ReportFormatEnum.PDF)

            logger.info(f"PDF report generated successfully: batch_id={batch_id}, path={report_path}")
            return report_path
        except ApplicationException:
            raise
        except Exception as e:
            logger.exception(f"Failed to generate PDF report for batch {batch_id}: {e}")
            raise ApplicationException(f"Ошибка при генерации PDF отчета: {e}") from e

    async def generate_excel_report(self, batch_id: UUID) -> str:
        """Генерирует Excel отчет для партии"""
        logger.info(f"Generating Excel report for batch: batch_id={batch_id}")

        try:
            batch_data = await self._report_data_service.get_batch_report_data(batch_id)

            excel_content = await self._excel_generator.generate(batch_data)

            report_path = await self._report_storage.save_report(batch_id, excel_content, ReportFormatEnum.EXCEL)

            logger.info(f"Excel report generated successfully: batch_id={batch_id}, path={report_path}")
            return report_path
        except ApplicationException:
            raise
        except Exception as e:
            logger.exception(f"Failed to generate Excel report for batch {batch_id}: {e}")
            raise ApplicationException(f"Ошибка при генерации Excel отчета: {e}") from e
