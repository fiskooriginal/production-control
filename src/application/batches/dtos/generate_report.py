from dataclasses import dataclass
from uuid import UUID

from src.application.batches.reports.dtos import ReportFormatEnum


@dataclass(frozen=True, slots=True, kw_only=True)
class GenerateReportInputDTO:
    batch_id: UUID
    format: ReportFormatEnum
