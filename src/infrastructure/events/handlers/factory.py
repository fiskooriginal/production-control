import inspect

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.batches.events.handlers import BatchCacheInvalidationHandler, BatchReportGenerationHandler
from src.application.batches.reports.adapters import ReportStorageAdapter
from src.application.batches.reports.services import ReportDataService, ReportGenerationService
from src.core.logging import get_logger
from src.infrastructure.background_tasks.app import get_cache_service, get_storage_service
from src.infrastructure.common.file_generators.batches.reports import BatchExcelReportGenerator, BatchPDFReportGenerator
from src.infrastructure.common.uow.unit_of_work import SqlAlchemyUnitOfWork
from src.infrastructure.persistence.queries.batches import BatchQueryService
from src.infrastructure.persistence.queries.work_centers import WorkCenterQueryService

logger = get_logger("events.handlers.factory")


def create_handler_instance(handler_class: type, session: AsyncSession) -> Any:
    """
    Создает экземпляр хендлера с внедрением всех необходимых зависимостей.

    Args:
        handler_class: Класс хендлера
        session: AsyncSession для создания зависимостей

    Returns:
        Экземпляр хендлера с инициализированными зависимостями
    """
    if handler_class == BatchReportGenerationHandler:
        return _create_batch_report_generation_handler(session)
    elif handler_class == BatchCacheInvalidationHandler:
        return _create_batch_cache_invalidation_handler()
    else:
        sig = inspect.signature(handler_class.__init__)
        params = list(sig.parameters.keys())[1:]
        if not params:
            return handler_class()
        raise ValueError(f"Cannot create instance of {handler_class.__name__}: unknown dependencies: {params}")


def _create_batch_report_generation_handler(session: AsyncSession) -> BatchReportGenerationHandler:
    """Создает экземпляр BatchClosedHandler со всеми зависимостями"""
    uow = SqlAlchemyUnitOfWork(session)
    batch_query_service = BatchQueryService(session)
    work_center_query_service = WorkCenterQueryService(session)
    report_data_service = ReportDataService(batch_query_service, work_center_query_service)
    pdf_generator = BatchPDFReportGenerator()
    excel_generator = BatchExcelReportGenerator()
    storage_service = get_storage_service()
    report_storage = ReportStorageAdapter(storage_service, bucket_name="reports")
    report_generation_service = ReportGenerationService(
        uow=uow,
        report_data_service=report_data_service,
        pdf_generator=pdf_generator,
        excel_generator=excel_generator,
        report_storage=report_storage,
    )
    return BatchReportGenerationHandler(report_generation_service)


def _create_batch_cache_invalidation_handler() -> BatchCacheInvalidationHandler:
    """Создает экземпляр BatchCacheInvalidationHandler с cache service"""
    cache_service = get_cache_service()
    return BatchCacheInvalidationHandler(cache_service)
