"""
Фабрика для создания экземпляров обработчиков событий с внедрением зависимостей.

Создает экземпляры хендлеров на основе их типов и доступных ресурсов в Celery worker.
"""

import inspect

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.batches.events.handlers.batch_closed_handler import GenerateReportOnBatchClosedHandler
from src.application.batches.reports.adapters import ReportStorageAdapter
from src.application.batches.reports.services import ReportDataService, ReportGenerationService
from src.application.work_centers.events.handlers.work_center_deleted_handler import WorkCenterDeletedHandler
from src.core.logging import get_logger
from src.infrastructure.background_tasks.app import get_cache_service, get_storage_service
from src.infrastructure.common.file_generators.batches.reports import BatchExcelReportGenerator, BatchPDFReportGenerator
from src.infrastructure.common.uow.unit_of_work import SqlAlchemyUnitOfWork
from src.infrastructure.persistence.queries import BatchQueryService, WorkCenterQueryService

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
    if handler_class == GenerateReportOnBatchClosedHandler:
        return _create_report_generation_handler(session)
    elif handler_class == WorkCenterDeletedHandler:
        return _create_work_center_deleted_handler()
    else:
        sig = inspect.signature(handler_class.__init__)
        params = list(sig.parameters.keys())[1:]
        if not params:
            return handler_class()
        raise ValueError(f"Cannot create instance of {handler_class.__name__}: unknown dependencies: {params}")


def _create_report_generation_handler(session: AsyncSession) -> GenerateReportOnBatchClosedHandler:
    """Создает экземпляр GenerateReportOnBatchClosedHandler со всеми зависимостями"""
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
    return GenerateReportOnBatchClosedHandler(report_generation_service)


def _create_work_center_deleted_handler() -> WorkCenterDeletedHandler:
    """Создает экземпляр WorkCenterDeletedHandler с cache service"""
    cache_service = get_cache_service()
    if cache_service is None:
        logger.warning("Cache service is not available, WorkCenterDeletedHandler will not work properly")
    return WorkCenterDeletedHandler(cache_service)
