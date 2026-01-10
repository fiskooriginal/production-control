from typing import Annotated

from fastapi import Depends

from src.application.products.queries.handlers import GetProductQueryHandler, ListProductsQueryHandler
from src.infrastructure.persistence.queries.products import ProductQueryService
from src.presentation.v1.common.di import async_session


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


list_products = Annotated[ListProductsQueryHandler, Depends(get_list_products_query_handler)]
get_product = Annotated[GetProductQueryHandler, Depends(get_product_query_handler)]
