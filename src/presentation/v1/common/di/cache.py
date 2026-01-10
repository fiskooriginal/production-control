from typing import Annotated

from fastapi import Depends, Request

from src.application.common.cache.interfaces import CacheServiceProtocol


async def get_cache_service(request: Request) -> CacheServiceProtocol | None:
    """Dependency для получения CacheService из app.state."""
    return getattr(request.app.state, "cache_service", None)


cache = Annotated[CacheServiceProtocol | None, Depends(get_cache_service)]
