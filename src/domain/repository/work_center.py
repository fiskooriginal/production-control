from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from src.domain.entities.work_center import WorkCenterEntity
from src.domain.shared.query import PaginationSpec, QueryResult, SortSpec


@dataclass(frozen=True, slots=True, kw_only=True)
class WorkCenterFilters:
    pass


class WorkCenterRepositoryProtocol(Protocol):
    async def create(self, work_center: WorkCenterEntity) -> WorkCenterEntity: ...

    async def get(self, uuid: UUID) -> WorkCenterEntity | None: ...

    async def exists(self, identifier: str) -> bool: ...

    async def update(self, uuid: UUID, work_center: WorkCenterEntity) -> WorkCenterEntity | None: ...

    async def delete(self, uuid: UUID) -> bool: ...

    async def list(
        self,
        filters: WorkCenterFilters | None = None,
        pagination: PaginationSpec | None = None,
        sort: SortSpec | None = None,
    ) -> QueryResult[WorkCenterEntity]: ...
