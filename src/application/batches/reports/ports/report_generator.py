from typing import Protocol

from src.application.batches.reports.models import BatchReportData


class ReportGeneratorProtocol(Protocol):
    """Протокол для генераторов отчетов"""

    async def generate(self, batch_data: BatchReportData) -> bytes:
        """Генерирует отчет в виде байтов"""
        ...
