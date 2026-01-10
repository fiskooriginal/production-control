from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_session(request: Request) -> AsyncGenerator[AsyncSession]:
    """Dependency для получения сессии БД"""
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        yield session


async_session = Annotated[AsyncSession, Depends(get_session)]
