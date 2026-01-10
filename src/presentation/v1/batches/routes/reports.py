from uuid import UUID

from fastapi import APIRouter, Query, status

from src.application.batches.dtos.generate_report import GenerateReportInputDTO
from src.application.batches.reports.dtos import ReportFormatEnum
from src.presentation.v1.batches.di.reports import generate_report_command
from src.presentation.v1.batches.schemas.responses import GenerateReportResponse

router = APIRouter()


@router.post(
    "/{batch_id}/reports/generate",
    response_model=GenerateReportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_report(
    batch_id: UUID,
    command: generate_report_command,
    format: ReportFormatEnum = Query(..., description="Формат отчета (pdf или excel)"),
    user_email: str | None = Query(None, description="Email адрес для отправки уведомления с отчетом"),
) -> GenerateReportResponse:
    """
    Генерирует отчет для партии
    """
    input_dto = GenerateReportInputDTO(batch_id=batch_id, format=format, user_email=user_email)
    result = await command.execute(input_dto)

    return GenerateReportResponse(report_path=result.report_path, download_url=result.download_url)
