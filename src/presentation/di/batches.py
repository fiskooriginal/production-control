from typing import Annotated

from fastapi import Depends

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
from src.infrastructure.persistence.queries import BatchQueryService, CachedBatchQueryService
from src.presentation.di.common import async_session, cache, uow


# Commands
async def get_create_batch_command(uow: uow, cache_service: cache) -> CreateBatchCommand:
    """Dependency для CreateBatchCommand"""
    return CreateBatchCommand(uow, cache_service)


async def get_close_batch_command(uow: uow, cache_service: cache) -> CloseBatchCommand:
    """Dependency для CloseBatchCommand"""
    return CloseBatchCommand(uow, cache_service)


async def get_add_product_to_batch_command(uow: uow, cache_service: cache) -> AddProductToBatchCommand:
    """Dependency для AddProductToBatchCommand"""
    return AddProductToBatchCommand(uow, cache_service)


async def get_remove_product_from_batch_command(uow: uow, cache_service: cache) -> RemoveProductFromBatchCommand:
    """Dependency для RemoveProductFromBatchCommand"""
    return RemoveProductFromBatchCommand(uow, cache_service)


async def get_aggregate_batch_command(uow: uow, cache_service: cache) -> AggregateBatchCommand:
    """Dependency для AggregateBatchCommand"""
    return AggregateBatchCommand(uow, cache_service)


async def get_update_batch_command(uow: uow, cache_service: cache) -> UpdateBatchCommand:
    """Dependency для UpdateBatchCommand"""
    return UpdateBatchCommand(uow, cache_service)


async def get_delete_batch_command(uow: uow, cache_service: cache) -> DeleteBatchCommand:
    """Dependency для DeleteBatchCommand"""
    return DeleteBatchCommand(uow, cache_service)


# Query Services
async def get_batch_query_service(session: async_session, cache_service: cache) -> BatchQueryService:
    """Dependency для BatchQueryService с кэшированием."""
    if cache_service and cache_service.enabled:
        return CachedBatchQueryService(session, cache_service)
    return BatchQueryService(session)


batch_query = Annotated[BatchQueryService, Depends(get_batch_query_service)]


async def get_list_batches_query_handler(query_service: batch_query) -> ListBatchesQueryHandler:
    """Dependency для ListBatchesQueryHandler"""
    return ListBatchesQueryHandler(query_service)


async def get_batch_query_handler(query_service: batch_query) -> GetBatchQueryHandler:
    """Dependency для GetBatchQueryHandler"""
    return GetBatchQueryHandler(query_service)


# Query Handlers
list_batches = Annotated[ListBatchesQueryHandler, Depends(get_list_batches_query_handler)]
get_batch = Annotated[GetBatchQueryHandler, Depends(get_batch_query_handler)]

# Commands
create_batch = Annotated[CreateBatchCommand, Depends(get_create_batch_command)]
close_batch = Annotated[CloseBatchCommand, Depends(get_close_batch_command)]
add_product_to_batch = Annotated[AddProductToBatchCommand, Depends(get_add_product_to_batch_command)]
remove_product_from_batch = Annotated[RemoveProductFromBatchCommand, Depends(get_remove_product_from_batch_command)]
aggregate_batch = Annotated[AggregateBatchCommand, Depends(get_aggregate_batch_command)]
update_batch = Annotated[UpdateBatchCommand, Depends(get_update_batch_command)]
delete_batch = Annotated[DeleteBatchCommand, Depends(get_delete_batch_command)]
