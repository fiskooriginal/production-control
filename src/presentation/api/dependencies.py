from collections.abc import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.batches.queries.use_cases import GetBatchQueryUseCase, ListBatchesQueryUseCase
from src.application.batches.use_cases import (
    AddProductToBatchUseCase,
    CloseBatchUseCase,
    CreateBatchUseCase,
    RemoveProductFromBatchUseCase,
)
from src.application.common.uow import UnitOfWorkProtocol
from src.application.products.queries.use_cases import GetProductQueryUseCase, ListProductsQueryUseCase
from src.application.products.use_cases import AggregateProductUseCase
from src.application.work_centers.queries.use_cases import GetWorkCenterQueryUseCase, ListWorkCentersQueryUseCase
from src.application.work_centers.use_cases import (
    CreateWorkCenterUseCase,
    DeleteWorkCenterUseCase,
    UpdateWorkCenterUseCase,
)
from src.infrastructure.persistence.queries import BatchQueryService, ProductQueryService, WorkCenterQueryService
from src.infrastructure.uow.unit_of_work import SqlAlchemyUnitOfWork


async def get_session(request: Request) -> AsyncGenerator[AsyncSession]:
    """Dependency для получения сессии БД"""
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        yield session


async def get_uow(session: AsyncSession = Depends(get_session)) -> UnitOfWorkProtocol:
    """Dependency для получения Unit of Work"""
    return SqlAlchemyUnitOfWork(session)


async def get_create_batch_use_case(uow: UnitOfWorkProtocol = Depends(get_uow)) -> CreateBatchUseCase:
    """Dependency для CreateBatchUseCase"""
    return CreateBatchUseCase(uow)


async def get_close_batch_use_case(uow: UnitOfWorkProtocol = Depends(get_uow)) -> CloseBatchUseCase:
    """Dependency для CloseBatchUseCase"""
    return CloseBatchUseCase(uow)


async def get_aggregate_product_use_case(uow: UnitOfWorkProtocol = Depends(get_uow)) -> AggregateProductUseCase:
    """Dependency для AggregateProductUseCase"""
    return AggregateProductUseCase(uow)


async def get_add_product_to_batch_use_case(uow: UnitOfWorkProtocol = Depends(get_uow)) -> AddProductToBatchUseCase:
    """Dependency для AddProductToBatchUseCase"""
    return AddProductToBatchUseCase(uow)


async def get_remove_product_from_batch_use_case(
    uow: UnitOfWorkProtocol = Depends(get_uow),
) -> RemoveProductFromBatchUseCase:
    """Dependency для RemoveProductFromBatchUseCase"""
    return RemoveProductFromBatchUseCase(uow)


async def get_create_work_center_use_case(uow: UnitOfWorkProtocol = Depends(get_uow)) -> CreateWorkCenterUseCase:
    """Dependency для CreateWorkCenterUseCase"""
    return CreateWorkCenterUseCase(uow)


async def get_update_work_center_use_case(uow: UnitOfWorkProtocol = Depends(get_uow)) -> UpdateWorkCenterUseCase:
    """Dependency для UpdateWorkCenterUseCase"""
    return UpdateWorkCenterUseCase(uow)


async def get_delete_work_center_use_case(uow: UnitOfWorkProtocol = Depends(get_uow)) -> DeleteWorkCenterUseCase:
    """Dependency для DeleteWorkCenterUseCase"""
    return DeleteWorkCenterUseCase(uow)


async def get_work_center_query_service(session: AsyncSession = Depends(get_session)) -> WorkCenterQueryService:
    """Dependency для WorkCenterQueryService"""
    return WorkCenterQueryService(session)


async def get_batch_query_service(session: AsyncSession = Depends(get_session)) -> BatchQueryService:
    """Dependency для BatchQueryService"""
    return BatchQueryService(session)


async def get_product_query_service(session: AsyncSession = Depends(get_session)) -> ProductQueryService:
    """Dependency для ProductQueryService"""
    return ProductQueryService(session)


async def get_list_work_centers_query_use_case(
    query_service: WorkCenterQueryService = Depends(get_work_center_query_service),
) -> ListWorkCentersQueryUseCase:
    """Dependency для ListWorkCentersQueryUseCase"""
    return ListWorkCentersQueryUseCase(query_service)


async def get_list_batches_query_use_case(
    query_service: BatchQueryService = Depends(get_batch_query_service),
) -> ListBatchesQueryUseCase:
    """Dependency для ListBatchesQueryUseCase"""
    return ListBatchesQueryUseCase(query_service)


async def get_list_products_query_use_case(
    query_service: ProductQueryService = Depends(get_product_query_service),
) -> ListProductsQueryUseCase:
    """Dependency для ListProductsQueryUseCase"""
    return ListProductsQueryUseCase(query_service)


async def get_work_center_query_use_case(
    query_service: WorkCenterQueryService = Depends(get_work_center_query_service),
) -> GetWorkCenterQueryUseCase:
    """Dependency для GetWorkCenterQueryUseCase"""
    return GetWorkCenterQueryUseCase(query_service)


async def get_batch_query_use_case(
    query_service: BatchQueryService = Depends(get_batch_query_service),
) -> GetBatchQueryUseCase:
    """Dependency для GetBatchQueryUseCase"""
    return GetBatchQueryUseCase(query_service)


async def get_product_query_use_case(
    query_service: ProductQueryService = Depends(get_product_query_service),
) -> GetProductQueryUseCase:
    """Dependency для GetProductQueryUseCase"""
    return GetProductQueryUseCase(query_service)
