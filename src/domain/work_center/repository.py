from typing import Protocol
from uuid import UUID

from src.domain.shared.query import PaginationSpec, QueryResult, SortSpec
from src.domain.work_center.entity import WorkCenterEntity


class WorkCenterRepositoryProtocol(Protocol):
    async def create(self, work_center: WorkCenterEntity) -> WorkCenterEntity: ...

    async def get(self, uuid: UUID) -> WorkCenterEntity | None: ...

    async def exists(self, identifier: str) -> bool: ...

    async def update(self, uuid: UUID, work_center: WorkCenterEntity) -> WorkCenterEntity | None: ...

    async def delete(self, uuid: UUID) -> bool: ...

    async def list(
        self,
        pagination: PaginationSpec | None = None,
        sort: SortSpec | None = None,
    ) -> QueryResult[WorkCenterEntity]: ...
