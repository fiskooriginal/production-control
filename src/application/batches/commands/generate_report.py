from src.application.batches.dtos.generate_report import GenerateReportInputDTO, GenerateReportOutputDTO
from src.application.batches.reports.adapters import ReportStorageAdapter
from src.application.batches.reports.services import ReportEmailService, ReportGenerationService
from src.application.common.exceptions import ApplicationException
from src.core.logging import get_logger

logger = get_logger("command.reports")


class GenerateReportCommand:
    """Обработчик команды генерации отчета"""

    def __init__(
        self,
        report_generation_service: ReportGenerationService,
        report_storage: ReportStorageAdapter,
        report_email_service: ReportEmailService | None = None,
    ) -> None:
        self._report_generation_service = report_generation_service
        self._report_storage = report_storage
        self._report_email_service = report_email_service

    async def execute(self, input_dto: GenerateReportInputDTO) -> GenerateReportOutputDTO:
        """Выполняет команду генерации отчета"""
        logger.info(f"Executing GenerateReportInputDTO: batch_id={input_dto.batch_id}, format={input_dto.format.value}")
        try:
            report_path = await self._report_generation_service.generate_report(input_dto.batch_id, input_dto.format)

            download_url = await self._report_storage.get_presigned_url(report_path)

            logger.info(
                f"Report generated successfully: batch_id={input_dto.batch_id}, path={report_path}, download_url generated"
            )

            if input_dto.user_email and self._report_email_service:
                await self._report_email_service.send_email(
                    user_email=input_dto.user_email,
                    batch_id=input_dto.batch_id,
                    format=input_dto.format,
                    report_path=report_path,
                )

            return GenerateReportOutputDTO(report_path=report_path, download_url=download_url)
        except ApplicationException:
            raise
        except Exception as e:
            logger.exception(f"Failed to execute GenerateReportInputDTO for batch {input_dto.batch_id}: {e}")
            raise ApplicationException(f"Ошибка при генерации отчета: {e}") from e
