from dataclasses import dataclass
from enum import Enum

from src.application.batches.reports.statistics import ReportStatisticsDTO
from src.domain.batches import BatchEntity


class ReportFormatEnum(str, Enum):
    PDF = "pdf"
    XLSX = "xlsx"


@dataclass(frozen=True, slots=True, kw_only=True)
class BatchReportDataDTO:
    batch: BatchEntity
    statistics: ReportStatisticsDTO
    work_center_name: str | None
