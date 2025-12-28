from collections.abc import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.batches.commands import (
    AddProductToBatchCommand,
    AggregateBatchCommand,
    CloseBatchCommand,
    CreateBatchCommand,
    DeleteBatchCommand,
    RemoveProductFromBatchCommand,
    UpdateBatchCommand,
)
from src.application.batches.queries.handlers import GetBatchQueryHandler, ListBatchesQueryHandler
from src.application.common.uow import UnitOfWorkProtocol
from src.application.products.commands import AggregateProductCommand
from src.application.products.queries.handlers import GetProductQueryHandler, ListProductsQueryHandler
from src.application.work_centers.commands import (
    CreateWorkCenterCommand,
    DeleteWorkCenterCommand,
    UpdateWorkCenterCommand,
)
from src.application.work_centers.queries.handlers import GetWorkCenterQueryHandler, ListWorkCentersQueryHandler
from src.infrastructure.cache.protocol import CacheServiceProtocol
from src.infrastructure.persistence.queries import (
    BatchQueryService,
    CachedBatchQueryService,
    ProductQueryService,
    WorkCenterQueryService,
)
from src.infrastructure.uow.unit_of_work import SqlAlchemyUnitOfWork

# Session


async def get_session(request: Request) -> AsyncGenerator[AsyncSession]:
    """Dependency для получения сессии БД"""
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        yield session


# Unit of Work


async def get_uow(session: AsyncSession = Depends(get_session)) -> UnitOfWorkProtocol:
    """Dependency для получения Unit of Work"""
    return SqlAlchemyUnitOfWork(session)


# Cache Service


async def get_cache_service(request: Request) -> CacheServiceProtocol | None:
    """Dependency для получения CacheService из app.state."""
    return getattr(request.app.state, "cache_service", None)


# Commands


# Batches
async def get_create_batch_command(
    uow: UnitOfWorkProtocol = Depends(get_uow),
    cache_service: CacheServiceProtocol | None = Depends(get_cache_service),
) -> CreateBatchCommand:
    """Dependency для CreateBatchCommand"""
    return CreateBatchCommand(uow, cache_service)


async def get_close_batch_command(
    uow: UnitOfWorkProtocol = Depends(get_uow),
    cache_service: CacheServiceProtocol | None = Depends(get_cache_service),
) -> CloseBatchCommand:
    """Dependency для CloseBatchCommand"""
    return CloseBatchCommand(uow, cache_service)


async def get_add_product_to_batch_command(
    uow: UnitOfWorkProtocol = Depends(get_uow),
    cache_service: CacheServiceProtocol | None = Depends(get_cache_service),
) -> AddProductToBatchCommand:
    """Dependency для AddProductToBatchCommand"""
    return AddProductToBatchCommand(uow, cache_service)


async def get_remove_product_from_batch_command(
    uow: UnitOfWorkProtocol = Depends(get_uow),
    cache_service: CacheServiceProtocol | None = Depends(get_cache_service),
) -> RemoveProductFromBatchCommand:
    """Dependency для RemoveProductFromBatchCommand"""
    return RemoveProductFromBatchCommand(uow, cache_service)


async def get_aggregate_batch_command(
    uow: UnitOfWorkProtocol = Depends(get_uow),
    cache_service: CacheServiceProtocol | None = Depends(get_cache_service),
) -> AggregateBatchCommand:
    """Dependency для AggregateBatchCommand"""
    return AggregateBatchCommand(uow, cache_service)


async def get_update_batch_command(
    uow: UnitOfWorkProtocol = Depends(get_uow),
    cache_service: CacheServiceProtocol | None = Depends(get_cache_service),
) -> UpdateBatchCommand:
    """Dependency для UpdateBatchCommand"""
    return UpdateBatchCommand(uow, cache_service)


async def get_delete_batch_command(
    uow: UnitOfWorkProtocol = Depends(get_uow),
    cache_service: CacheServiceProtocol | None = Depends(get_cache_service),
) -> DeleteBatchCommand:
    """Dependency для DeleteBatchCommand"""
    return DeleteBatchCommand(uow, cache_service)


# Products
async def get_aggregate_product_command(uow: UnitOfWorkProtocol = Depends(get_uow)) -> AggregateProductCommand:
    """Dependency для AggregateProductCommand"""
    return AggregateProductCommand(uow)


# Work Centers
async def get_create_work_center_command(uow: UnitOfWorkProtocol = Depends(get_uow)) -> CreateWorkCenterCommand:
    """Dependency для CreateWorkCenterCommand"""
    return CreateWorkCenterCommand(uow)


async def get_update_work_center_command(uow: UnitOfWorkProtocol = Depends(get_uow)) -> UpdateWorkCenterCommand:
    """Dependency для UpdateWorkCenterCommand"""
    return UpdateWorkCenterCommand(uow)


async def get_delete_work_center_command(uow: UnitOfWorkProtocol = Depends(get_uow)) -> DeleteWorkCenterCommand:
    """Dependency для DeleteWorkCenterCommand"""
    return DeleteWorkCenterCommand(uow)


# Query Services


async def get_work_center_query_service(session: AsyncSession = Depends(get_session)) -> WorkCenterQueryService:
    """Dependency для WorkCenterQueryService"""
    return WorkCenterQueryService(session)


async def get_batch_query_service(
    session: AsyncSession = Depends(get_session),
    cache_service: CacheServiceProtocol | None = Depends(get_cache_service),
) -> BatchQueryService:
    """Dependency для BatchQueryService с кэшированием."""
    if cache_service and cache_service.enabled:
        return CachedBatchQueryService(session, cache_service)
    return BatchQueryService(session)


async def get_product_query_service(session: AsyncSession = Depends(get_session)) -> ProductQueryService:
    """Dependency для ProductQueryService"""
    return ProductQueryService(session)


async def get_list_work_centers_query_handler(
    query_service: WorkCenterQueryService = Depends(get_work_center_query_service),
) -> ListWorkCentersQueryHandler:
    """Dependency для ListWorkCentersQueryHandler"""
    return ListWorkCentersQueryHandler(query_service)


async def get_list_batches_query_handler(
    query_service: BatchQueryService = Depends(get_batch_query_service),
) -> ListBatchesQueryHandler:
    """Dependency для ListBatchesQueryHandler"""
    return ListBatchesQueryHandler(query_service)


async def get_list_products_query_handler(
    query_service: ProductQueryService = Depends(get_product_query_service),
) -> ListProductsQueryHandler:
    """Dependency для ListProductsQueryHandler"""
    return ListProductsQueryHandler(query_service)


async def get_work_center_query_handler(
    query_service: WorkCenterQueryService = Depends(get_work_center_query_service),
) -> GetWorkCenterQueryHandler:
    """Dependency для GetWorkCenterQueryHandler"""
    return GetWorkCenterQueryHandler(query_service)


async def get_batch_query_handler(
    query_service: BatchQueryService = Depends(get_batch_query_service),
) -> GetBatchQueryHandler:
    """Dependency для GetBatchQueryHandler"""
    return GetBatchQueryHandler(query_service)


async def get_product_query_handler(
    query_service: ProductQueryService = Depends(get_product_query_service),
) -> GetProductQueryHandler:
    """Dependency для GetProductQueryHandler"""
    return GetProductQueryHandler(query_service)
