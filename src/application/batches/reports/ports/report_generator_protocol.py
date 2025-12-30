from typing import Protocol

from src.application.batches.reports.dtos import BatchReportOutputDTO


class ReportGeneratorProtocol(Protocol):
    """Протокол для генераторов отчетов"""

    async def generate(self, batch_data: BatchReportOutputDTO) -> bytes:
        """Генерирует отчет в виде байтов"""
        ...
