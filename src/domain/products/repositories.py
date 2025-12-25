from typing import Protocol
from uuid import UUID

from src.domain.products.entities import ProductEntity
from src.domain.shared.repository_protocol import BaseRepositoryProtocol


class ProductRepositoryProtocol(BaseRepositoryProtocol[ProductEntity], Protocol):
    async def get_by_unique_code(self, unique_code: str) -> ProductEntity | None:
        """Возвращает продукт по уникальному коду."""
        ...

    async def get_aggregated(self) -> list[ProductEntity]:
        """Возвращает все агрегированные продукты."""
        ...

    async def get_by_ids(self, ids: list[UUID]) -> ProductEntity | None:
        """Возвращает все продукты из переданного списка ID"""
        ...
