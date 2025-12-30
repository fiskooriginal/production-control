from dataclasses import dataclass
from enum import Enum

from src.application.batches.queries import BatchReadDTO
from src.application.batches.reports.statistics import ReportStatistics


class ReportFormat(str, Enum):
    PDF = "pdf"
    EXCEL = "excel"


@dataclass(frozen=True, slots=True, kw_only=True)
class BatchReportData:
    batch: BatchReadDTO
    statistics: ReportStatistics
    work_center_name: str | None
