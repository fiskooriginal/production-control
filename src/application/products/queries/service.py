from typing import Protocol
from uuid import UUID

from src.application.products.queries.queries import ListProductsQuery
from src.domain.common.queries import QueryResult
from src.domain.products import ProductEntity


class ProductQueryServiceProtocol(Protocol):
    async def get(self, product_id: UUID) -> ProductEntity | None:
        """Получает продукт по UUID"""
        ...

    async def list(self, query: ListProductsQuery) -> QueryResult[ProductEntity]:
        """Получает список продуктов с пагинацией и сортировкой"""
        ...
