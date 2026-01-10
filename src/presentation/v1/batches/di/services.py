from typing import Annotated

from fastapi import Depends, Request

from src.application.batches.reports.adapters import ReportStorageAdapter
from src.application.batches.reports.ports import ReportGeneratorProtocol
from src.application.batches.reports.services import ReportDataService, ReportEmailService, ReportGenerationService
from src.application.common.email.interfaces import EmailServiceProtocol
from src.application.common.storage.interfaces import StorageServiceProtocol
from src.application.work_centers.queries.service import WorkCenterQueryServiceProtocol
from src.core.logging import get_logger
from src.core.settings import EmailSettings
from src.infrastructure.common.email.smtp import SMTPEmailService
from src.infrastructure.common.file_generators.batches.reports import BatchExcelReportGenerator, BatchPDFReportGenerator
from src.infrastructure.persistence.queries.work_centers import WorkCenterQueryService
from src.presentation.v1.batches.di.queries import batch_query
from src.presentation.v1.common.di import async_session, uow

logger = get_logger("di.reports")


async def get_storage_service(request: Request) -> StorageServiceProtocol:
    """Dependency для получения StorageService из app.state."""
    return getattr(request.app.state, "storage_service", None)


storage_service = Annotated[StorageServiceProtocol, Depends(get_storage_service)]


async def get_work_center_query_service(session: async_session) -> WorkCenterQueryServiceProtocol:
    """Dependency для получения WorkCenterQueryService."""
    return WorkCenterQueryService(session)


work_center_query = Annotated[WorkCenterQueryServiceProtocol, Depends(get_work_center_query_service)]


async def get_report_data_service(
    batch_query_service: batch_query,
    work_center_query_service: work_center_query,
) -> ReportDataService:
    """Dependency для получения ReportDataService."""
    return ReportDataService(batch_query_service, work_center_query_service)


async def get_pdf_generator() -> ReportGeneratorProtocol:
    """Dependency для получения PDF генератора."""
    return BatchPDFReportGenerator()


async def get_excel_generator() -> ReportGeneratorProtocol:
    """Dependency для получения Excel генератора."""
    return BatchExcelReportGenerator()


async def get_report_storage_adapter(storage: storage_service) -> ReportStorageAdapter:
    """Dependency для получения ReportStorageAdapter."""
    return ReportStorageAdapter(storage, bucket_name="reports")


report_storage = Annotated[ReportStorageAdapter, Depends(get_report_storage_adapter)]


async def get_report_generation_service(
    unit_of_work: uow,
    report_data_service: Annotated[ReportDataService, Depends(get_report_data_service)],
    pdf_generator: Annotated[ReportGeneratorProtocol, Depends(get_pdf_generator)],
    excel_generator: Annotated[ReportGeneratorProtocol, Depends(get_excel_generator)],
    report_storage: Annotated[ReportStorageAdapter, Depends(get_report_storage_adapter)],
) -> ReportGenerationService:
    """Dependency для получения ReportGenerationService."""
    return ReportGenerationService(
        uow=unit_of_work,
        report_data_service=report_data_service,
        pdf_generator=pdf_generator,
        excel_generator=excel_generator,
        report_storage=report_storage,
    )


report_generation_service = Annotated[ReportGenerationService, Depends(get_report_generation_service)]


async def get_email_service() -> EmailServiceProtocol | None:
    """Dependency для получения EmailServiceProtocol (если настроен)."""
    try:
        email_settings = EmailSettings()
        if email_settings.is_configured():
            return SMTPEmailService(email_settings)
        logger.info("Email service is not configured")
        return None
    except Exception as e:
        logger.warning(f"Failed to initialize email service: {e}")
        return None


email_service = Annotated[EmailServiceProtocol | None, Depends(get_email_service)]


async def get_report_email_service(
    email_service: email_service,
    report_storage: report_storage,
    batch_query_service: batch_query,
) -> ReportEmailService | None:
    """Dependency для получения ReportEmailService (если email настроен)."""
    if email_service is None:
        return None
    return ReportEmailService(
        email_service=email_service,
        report_storage=report_storage,
        batch_query_service=batch_query_service,
    )


report_email_service = Annotated[ReportEmailService | None, Depends(get_report_email_service)]
