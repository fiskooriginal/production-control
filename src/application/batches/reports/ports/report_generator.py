from typing import Protocol

from src.application.batches.reports.dtos import BatchReportDataDTO


class ReportGeneratorProtocol(Protocol):
    """Протокол для генераторов отчетов"""

    def generate(self, batch_data: BatchReportDataDTO) -> bytes:
        """Генерирует отчет в виде байтов"""
        ...
