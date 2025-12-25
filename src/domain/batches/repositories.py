from typing import Any, Protocol
from uuid import UUID

from src.domain.batches.entities import BatchEntity
from src.domain.shared.queries import PaginationSpec, QueryResult, SortSpec
from src.domain.shared.repository_protocol import BaseRepositoryProtocol


class BatchRepositoryProtocol(BaseRepositoryProtocol[BatchEntity], Protocol):
    async def get_by_batch_number(self, batch_number: int) -> BatchEntity | None:
        """Находит партию по номеру партии."""
        ...

    async def get_by_work_center(self, work_center_uuid: UUID) -> list[BatchEntity]:
        """Находит все партии для указанного рабочего центра."""
        ...

    async def list(
        self,
        filters: dict[str, Any] | None = None,
        pagination: PaginationSpec | None = None,
        sort: SortSpec | None = None,
    ) -> QueryResult[BatchEntity]:
        """Получает список партий с фильтрацией, пагинацией и сортировкой."""
        ...
