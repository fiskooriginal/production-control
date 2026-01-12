from typing import Annotated

from fastapi import Depends

from src.application.batches.queries.handlers import GetBatchQueryHandler, ListBatchesQueryHandler
from src.infrastructure.persistence.queries.batches import BatchQueryService, CachedBatchQueryServiceProxy
from src.presentation.v1.common.di import async_session, cache


async def get_batch_query_service(session: async_session, cache_service: cache) -> BatchQueryService:
    """Dependency для BatchQueryService с кэшированием."""
    if cache_service and cache_service.enabled:
        return CachedBatchQueryServiceProxy(session, cache_service)
    return BatchQueryService(session)


batch_query = Annotated[BatchQueryService, Depends(get_batch_query_service)]


async def get_list_batches_query_handler(query_service: batch_query) -> ListBatchesQueryHandler:
    """Dependency для ListBatchesQueryHandler"""
    return ListBatchesQueryHandler(query_service)


async def get_batch_query_handler(query_service: batch_query) -> GetBatchQueryHandler:
    """Dependency для GetBatchQueryHandler"""
    return GetBatchQueryHandler(query_service)


list_batches = Annotated[ListBatchesQueryHandler, Depends(get_list_batches_query_handler)]
get_batch = Annotated[GetBatchQueryHandler, Depends(get_batch_query_handler)]
