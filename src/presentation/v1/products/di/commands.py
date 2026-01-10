from typing import Annotated

from fastapi import Depends

from src.application.products.commands.aggregate_product import AggregateProductCommand
from src.presentation.v1.common.di import uow


async def get_aggregate_product_command(unit_of_work: uow) -> AggregateProductCommand:
    """Dependency для AggregateProductCommand"""
    return AggregateProductCommand(unit_of_work)


aggregate_product = Annotated[AggregateProductCommand, Depends(get_aggregate_product_command)]
