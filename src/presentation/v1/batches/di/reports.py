from typing import Annotated

from fastapi import Depends

from src.application.batches.commands.generate_report import GenerateReportCommand
from src.presentation.v1.batches.di.services import report_email_service, report_generation_service, report_storage


async def get_generate_report_command(
    report_generation_service: report_generation_service,
    report_storage: report_storage,
    report_email_service: report_email_service,
) -> GenerateReportCommand:
    """Dependency для получения GenerateReportCommand."""
    return GenerateReportCommand(
        report_generation_service=report_generation_service,
        report_storage=report_storage,
        report_email_service=report_email_service,
    )


generate_report_command = Annotated[GenerateReportCommand, Depends(get_generate_report_command)]
