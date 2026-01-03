from src.infrastructure.common.exceptions import InfrastructureException


class BatchReportGenerationError(InfrastructureException):
    """Исключение для ошибок генерации отчетов батчей."""


class BatchExcelGenerationError(BatchReportGenerationError):
    """Исключение для ошибок генерации Excel отчетов батчей."""


class BatchPDFGenerationError(BatchReportGenerationError):
    """Исключение для ошибок генерации PDF отчетов батчей."""
