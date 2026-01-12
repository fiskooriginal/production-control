from typing import ClassVar

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.products.queries.queries import ListProductsQuery
from src.application.products.queries.service import ProductQueryServiceProtocol
from src.application.products.queries.sort import ProductSortField
from src.domain.products import ProductEntity
from src.infrastructure.persistence.mappers.products import to_domain_entity
from src.infrastructure.persistence.models.product import Product
from src.infrastructure.persistence.queries.base import BaseQueryService


class ProductQueryService(
    BaseQueryService[ProductEntity, Product, ListProductsQuery, None, ProductSortField],
    ProductQueryServiceProtocol,
):
    SORT_FIELD_MAPPING: ClassVar = {
        ProductSortField.CREATED_AT: Product.created_at,
        ProductSortField.UPDATED_AT: Product.updated_at,
        ProductSortField.UNIQUE_CODE: Product.unique_code,
        ProductSortField.IS_AGGREGATED: Product.is_aggregated,
        ProductSortField.AGGREGATED_AT: Product.aggregated_at,
    }

    def __init__(self, session: AsyncSession):
        super().__init__(session, Product, to_domain_entity)
