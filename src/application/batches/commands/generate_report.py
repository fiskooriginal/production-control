from src.application.batches.dtos.generate_report import GenerateReportInputDTO
from src.application.batches.reports.services.report_generation_service import ReportGenerationService
from src.application.common.exceptions import ApplicationException
from src.core.logging import get_logger

logger = get_logger("command.reports")


class GenerateReportCommand:
    """Обработчик команды генерации отчета"""

    def __init__(self, report_generation_service: ReportGenerationService) -> None:
        self._report_generation_service = report_generation_service

    async def execute(self, command: GenerateReportInputDTO) -> str:
        """Выполняет команду генерации отчета"""
        logger.info(f"Executing GenerateReportInputDTO: batch_id={command.batch_id}, format={command.format.value}")
        try:
            report_path = await self._report_generation_service.generate_report(command.batch_id, command.format)
            logger.info(f"Report generated successfully: batch_id={command.batch_id}, path={report_path}")
            return report_path
        except ApplicationException:
            raise
        except Exception as e:
            logger.exception(f"Failed to execute GenerateReportInputDTO for batch {command.batch_id}: {e}")
            raise ApplicationException(f"Ошибка при генерации отчета: {e}") from e
