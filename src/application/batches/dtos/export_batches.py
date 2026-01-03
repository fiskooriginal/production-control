from dataclasses import dataclass

from src.application.batches.queries.filters import BatchReadFilters
from src.application.common.dtos import ExportImportFileFormatEnum


@dataclass
class ExportBatchesInputDTO:
    format: ExportImportFileFormatEnum
    filters: BatchReadFilters


@dataclass
class ExportBatchesOutputDTO:
    total_batches: int
    file_url: str
    presigned_url: str
