from typing import Protocol
from uuid import UUID

from src.domain.common.repository_protocol import BaseRepositoryProtocol
from src.domain.products.entities import ProductEntity


class ProductRepositoryProtocol(BaseRepositoryProtocol[ProductEntity], Protocol):
    async def get_by_unique_code(self, unique_code: str) -> ProductEntity | None:
        """Возвращает продукт по уникальному коду."""
        ...

    async def get_aggregated(self) -> list[ProductEntity]:
        """Возвращает все агрегированные продукты."""
        ...

    async def get_by_ids(self, ids: list[UUID]) -> list[ProductEntity]:
        """Возвращает все продукты из переданного списка ID."""
        ...

    async def get_by_unique_codes(self, unique_codes: list[str]) -> list[ProductEntity]:
        """Возвращает все продукты из переданного списка уникальных кодов."""
        ...
