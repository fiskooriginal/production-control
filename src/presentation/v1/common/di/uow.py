from typing import Annotated

from fastapi import Depends

from src.application.common.uow.interfaces import UnitOfWorkProtocol
from src.infrastructure.common.uow import SqlAlchemyUnitOfWork
from src.presentation.v1.common.di.session import async_session


async def get_uow(session: async_session) -> UnitOfWorkProtocol:
    """Dependency для получения Unit of Work"""
    return SqlAlchemyUnitOfWork(session)


uow = Annotated[UnitOfWorkProtocol, Depends(get_uow)]
