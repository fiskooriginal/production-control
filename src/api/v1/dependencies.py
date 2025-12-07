from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker


def get_engine(request: Request) -> AsyncEngine:
    if not hasattr(request.app.state, "engine"):
        raise RuntimeError("Engine not initialized. Check lifespan configuration.")
    return request.app.state.engine


def get_session_factory(request: Request) -> async_sessionmaker[AsyncSession]:
    if not hasattr(request.app.state, "session_factory"):
        raise RuntimeError("Session factory not initialized. Check lifespan configuration.")
    return request.app.state.session_factory


async def get_db_session(
    session_factory: Annotated[async_sessionmaker[AsyncSession], Depends(get_session_factory)],
) -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session


DBEngine: type[AsyncEngine] = Annotated[AsyncEngine, Depends(get_engine)]
DBSession: type[AsyncSession] = Annotated[AsyncSession, Depends(get_db_session)]
