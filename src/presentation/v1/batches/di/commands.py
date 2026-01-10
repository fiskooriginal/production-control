from typing import Annotated

from fastapi import Depends

from src.application.batches.commands.add_product import AddProductToBatchCommand
from src.application.batches.commands.aggregate import AggregateBatchCommand
from src.application.batches.commands.close import CloseBatchCommand
from src.application.batches.commands.create import CreateBatchCommand
from src.application.batches.commands.delete import DeleteBatchCommand
from src.application.batches.commands.remove_product import RemoveProductFromBatchCommand
from src.application.batches.commands.update import UpdateBatchCommand
from src.presentation.v1.common.di import cache, uow


async def get_create_batch_command(unit_of_work: uow, cache_service: cache) -> CreateBatchCommand:
    """Dependency для CreateBatchCommand"""
    return CreateBatchCommand(unit_of_work, cache_service)


async def get_close_batch_command(unit_of_work: uow, cache_service: cache) -> CloseBatchCommand:
    """Dependency для CloseBatchCommand"""
    return CloseBatchCommand(unit_of_work, cache_service)


async def get_add_product_to_batch_command(unit_of_work: uow, cache_service: cache) -> AddProductToBatchCommand:
    """Dependency для AddProductToBatchCommand"""
    return AddProductToBatchCommand(unit_of_work, cache_service)


async def get_remove_product_from_batch_command(
    unit_of_work: uow, cache_service: cache
) -> RemoveProductFromBatchCommand:
    """Dependency для RemoveProductFromBatchCommand"""
    return RemoveProductFromBatchCommand(unit_of_work, cache_service)


async def get_aggregate_batch_command(unit_of_work: uow, cache_service: cache) -> AggregateBatchCommand:
    """Dependency для AggregateBatchCommand"""
    return AggregateBatchCommand(unit_of_work, cache_service)


async def get_update_batch_command(unit_of_work: uow, cache_service: cache) -> UpdateBatchCommand:
    """Dependency для UpdateBatchCommand"""
    return UpdateBatchCommand(unit_of_work, cache_service)


async def get_delete_batch_command(unit_of_work: uow, cache_service: cache) -> DeleteBatchCommand:
    """Dependency для DeleteBatchCommand"""
    return DeleteBatchCommand(unit_of_work, cache_service)


create_batch = Annotated[CreateBatchCommand, Depends(get_create_batch_command)]
close_batch = Annotated[CloseBatchCommand, Depends(get_close_batch_command)]
add_product_to_batch = Annotated[AddProductToBatchCommand, Depends(get_add_product_to_batch_command)]
remove_product_from_batch = Annotated[RemoveProductFromBatchCommand, Depends(get_remove_product_from_batch_command)]
aggregate_batch = Annotated[AggregateBatchCommand, Depends(get_aggregate_batch_command)]
update_batch = Annotated[UpdateBatchCommand, Depends(get_update_batch_command)]
delete_batch = Annotated[DeleteBatchCommand, Depends(get_delete_batch_command)]
