from typing import Annotated

from fastapi import Depends, Request

from src.application.batches.commands.generate_report import GenerateReportCommand
from src.application.batches.reports.adapters import ReportStorageAdapter
from src.application.batches.reports.ports import ReportGeneratorProtocol
from src.application.batches.reports.services import ReportDataService, ReportGenerationService
from src.application.common.storage.interface import StorageServiceProtocol
from src.application.work_centers.queries import WorkCenterQueryServiceProtocol
from src.infrastructure.persistence.queries import WorkCenterQueryService
from src.infrastructure.reports.generators import BatchExcelReportGenerator, BatchPDFReportGenerator
from src.presentation.di.batches import batch_query
from src.presentation.di.common import async_session


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
    return ReportStorageAdapter(storage, reports_prefix="reports")


async def get_report_generation_service(
    report_data_service: Annotated[ReportDataService, Depends(get_report_data_service)],
    pdf_generator: Annotated[ReportGeneratorProtocol, Depends(get_pdf_generator)],
    excel_generator: Annotated[ReportGeneratorProtocol, Depends(get_excel_generator)],
    report_storage: Annotated[ReportStorageAdapter, Depends(get_report_storage_adapter)],
) -> ReportGenerationService:
    """Dependency для получения ReportGenerationService."""
    return ReportGenerationService(
        report_data_service=report_data_service,
        pdf_generator=pdf_generator,
        excel_generator=excel_generator,
        report_storage=report_storage,
    )


async def get_generate_report_command(
    report_generation_service: Annotated[ReportGenerationService, Depends(get_report_generation_service)],
) -> GenerateReportCommand:
    """Dependency для получения GenerateReportCommand."""
    return GenerateReportCommand(report_generation_service)


generate_report_command = Annotated[GenerateReportCommand, Depends(get_generate_report_command)]
