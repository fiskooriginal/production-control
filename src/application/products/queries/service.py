from typing import Protocol
from uuid import UUID

from src.application.products.queries.dtos import ProductReadDTO
from src.application.products.queries.queries import ListProductsQuery
from src.domain.common.queries import QueryResult


class ProductQueryServiceProtocol(Protocol):
    async def get(self, product_id: UUID) -> ProductReadDTO | None:
        """Получает продукт по UUID"""
        ...

    async def list(self, query: ListProductsQuery) -> QueryResult[ProductReadDTO]:
        """Получает список продуктов с пагинацией и сортировкой"""
        ...
