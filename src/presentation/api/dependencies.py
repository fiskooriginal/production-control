from collections.abc import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.uow import UnitOfWork
from src.application.use_cases.batches import (
    AddProductToBatchUseCase,
    CloseBatchUseCase,
    CreateBatchUseCase,
    ListBatchesUseCase,
    RemoveProductFromBatchUseCase,
)
from src.application.use_cases.products import AggregateProductUseCase
from src.application.use_cases.work_centers import (
    CreateWorkCenterUseCase,
    DeleteWorkCenterUseCase,
    GetWorkCenterUseCase,
    ListWorkCentersUseCase,
    UpdateWorkCenterUseCase,
)


async def get_session(request: Request) -> AsyncGenerator[AsyncSession]:
    """Dependency для получения сессии БД"""
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        yield session


async def get_uow(session: AsyncSession = Depends(get_session)) -> UnitOfWork:
    """Dependency для получения Unit of Work"""
    return UnitOfWork(session)


async def get_create_batch_use_case(uow: UnitOfWork = Depends(get_uow)) -> CreateBatchUseCase:
    """Dependency для CreateBatchUseCase"""
    return CreateBatchUseCase(uow)


async def get_close_batch_use_case(uow: UnitOfWork = Depends(get_uow)) -> CloseBatchUseCase:
    """Dependency для CloseBatchUseCase"""
    return CloseBatchUseCase(uow)


async def get_aggregate_product_use_case(uow: UnitOfWork = Depends(get_uow)) -> AggregateProductUseCase:
    """Dependency для AggregateProductUseCase"""
    return AggregateProductUseCase(uow)


async def get_add_product_to_batch_use_case(uow: UnitOfWork = Depends(get_uow)) -> AddProductToBatchUseCase:
    """Dependency для AddProductToBatchUseCase"""
    return AddProductToBatchUseCase(uow)


async def get_remove_product_from_batch_use_case(uow: UnitOfWork = Depends(get_uow)) -> RemoveProductFromBatchUseCase:
    """Dependency для RemoveProductFromBatchUseCase"""
    return RemoveProductFromBatchUseCase(uow)


async def get_list_batches_use_case(uow: UnitOfWork = Depends(get_uow)) -> ListBatchesUseCase:
    """Dependency для ListBatchesUseCase"""
    return ListBatchesUseCase(uow)


async def get_create_work_center_use_case(uow: UnitOfWork = Depends(get_uow)) -> CreateWorkCenterUseCase:
    """Dependency для CreateWorkCenterUseCase"""
    return CreateWorkCenterUseCase(uow)


async def get_get_work_center_use_case(uow: UnitOfWork = Depends(get_uow)) -> GetWorkCenterUseCase:
    """Dependency для GetWorkCenterUseCase"""
    return GetWorkCenterUseCase(uow)


async def get_update_work_center_use_case(uow: UnitOfWork = Depends(get_uow)) -> UpdateWorkCenterUseCase:
    """Dependency для UpdateWorkCenterUseCase"""
    return UpdateWorkCenterUseCase(uow)


async def get_delete_work_center_use_case(uow: UnitOfWork = Depends(get_uow)) -> DeleteWorkCenterUseCase:
    """Dependency для DeleteWorkCenterUseCase"""
    return DeleteWorkCenterUseCase(uow)


async def get_list_work_centers_use_case(uow: UnitOfWork = Depends(get_uow)) -> ListWorkCentersUseCase:
    """Dependency для ListWorkCentersUseCase"""
    return ListWorkCentersUseCase(uow)
