from datetime import date
from typing import Protocol
from uuid import UUID

from src.domain.batch.entity import BatchEntity
from src.domain.batch.filter import BatchFilters
from src.domain.shared.query import PaginationSpec, QueryResult, SortSpec


class BatchRepositoryProtocol(Protocol):
    async def create(self, batch: BatchEntity) -> BatchEntity: ...

    async def get(self, uuid: UUID) -> BatchEntity | None: ...

    async def exists(self, batch_number: int, batch_date: date) -> bool: ...

    async def update(self, uuid: UUID, batch: BatchEntity) -> BatchEntity | None: ...

    async def delete(self, uuid: UUID) -> bool: ...

    async def list(
        self,
        filters: BatchFilters | None = None,
        pagination: PaginationSpec | None = None,
        sort: SortSpec | None = None,
    ) -> QueryResult[BatchEntity]: ...
