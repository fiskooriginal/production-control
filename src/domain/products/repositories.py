from typing import Protocol

from src.domain.products.entities import ProductEntity
from src.domain.shared.repository_protocol import BaseRepositoryProtocol


class ProductRepositoryProtocol(BaseRepositoryProtocol[ProductEntity], Protocol):
    async def get_by_unique_code(self, unique_code: str) -> ProductEntity | None:
        """Находит продукт по уникальному коду."""
        ...

    async def get_aggregated(self) -> list[ProductEntity]:
        """Находит все агрегированные продукты."""
        ...
