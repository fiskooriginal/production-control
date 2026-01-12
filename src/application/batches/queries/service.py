from typing import Protocol
from uuid import UUID

from src.application.batches.queries.queries import ListBatchesQuery
from src.domain.batches import BatchEntity
from src.domain.common.queries import QueryResult


class BatchQueryServiceProtocol(Protocol):
    async def get(self, batch_id: UUID) -> BatchEntity | None:
        """Получает партию по UUID"""
        ...

    async def list(self, query: ListBatchesQuery) -> QueryResult[BatchEntity]:
        """Получает список партий с фильтрацией, пагинацией и сортировкой"""
        ...
