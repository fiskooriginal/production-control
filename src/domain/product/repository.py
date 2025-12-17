from typing import Protocol
from uuid import UUID

from src.domain.product.entity import ProductEntity
from src.domain.shared.query import PaginationSpec, QueryResult, SortSpec


class ProductRepositoryProtocol(Protocol):
    async def create(self, product: ProductEntity) -> ProductEntity: ...

    async def get(self, uuid: UUID) -> ProductEntity | None: ...

    async def exists(self, unique_code: str) -> bool: ...

    async def update(self, uuid: UUID, product: ProductEntity) -> ProductEntity | None: ...

    async def delete(self, uuid: UUID) -> bool: ...

    async def list(
        self,
        pagination: PaginationSpec | None = None,
        sort: SortSpec | None = None,
    ) -> QueryResult[ProductEntity]: ...
