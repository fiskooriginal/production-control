from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.common.cache.interface.protocol import CacheServiceProtocol
from src.application.common.uow import UnitOfWorkProtocol
from src.infrastructure.uow.unit_of_work import SqlAlchemyUnitOfWork


async def get_session(request: Request) -> AsyncGenerator[AsyncSession]:
    """Dependency для получения сессии БД"""
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        yield session


async_session = Annotated[AsyncSession, Depends(get_session)]


async def get_uow(session: async_session) -> UnitOfWorkProtocol:
    """Dependency для получения Unit of Work"""
    return SqlAlchemyUnitOfWork(session)


uow = Annotated[UnitOfWorkProtocol, Depends(get_uow)]


async def get_cache_service(request: Request) -> CacheServiceProtocol | None:
    """Dependency для получения CacheService из app.state."""
    return getattr(request.app.state, "cache_service", None)


cache = Annotated[CacheServiceProtocol | None, Depends(get_cache_service)]
