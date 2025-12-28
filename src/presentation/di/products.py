from typing import Annotated

from fastapi import Depends

from src.application.products.commands import AggregateProductCommand
from src.application.products.queries.handlers import GetProductQueryHandler, ListProductsQueryHandler
from src.infrastructure.persistence.queries import ProductQueryService
from src.presentation.di.common import async_session, uow


# Commands
async def get_aggregate_product_command(uow: uow) -> AggregateProductCommand:
    """Dependency для AggregateProductCommand"""
    return AggregateProductCommand(uow)


# Query Services
async def get_product_query_service(session: async_session) -> ProductQueryService:
    """Dependency для ProductQueryService"""
    return ProductQueryService(session)


product_query = Annotated[ProductQueryService, Depends(get_product_query_service)]


async def get_list_products_query_handler(query_service: product_query) -> ListProductsQueryHandler:
    """Dependency для ListProductsQueryHandler"""
    return ListProductsQueryHandler(query_service)


async def get_product_query_handler(query_service: product_query) -> GetProductQueryHandler:
    """Dependency для GetProductQueryHandler"""
    return GetProductQueryHandler(query_service)


# Query Handlers
list_products = Annotated[ListProductsQueryHandler, Depends(get_list_products_query_handler)]
get_product = Annotated[GetProductQueryHandler, Depends(get_product_query_handler)]

# Commands
aggregate_product = Annotated[AggregateProductCommand, Depends(get_aggregate_product_command)]
