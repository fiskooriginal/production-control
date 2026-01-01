from dataclasses import dataclass
from uuid import UUID

from src.application.batches.reports.dtos import ReportFormatEnum


@dataclass(frozen=True, slots=True, kw_only=True)
class GenerateReportInputDTO:
    batch_id: UUID
    format: ReportFormatEnum
    user_email: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class GenerateReportOutputDTO:
    report_path: str
    download_url: str
