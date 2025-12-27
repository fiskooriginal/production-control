from typing import Protocol
from uuid import UUID

from src.application.batches.queries.dtos import BatchReadDTO
from src.application.batches.queries.queries import ListBatchesQuery
from src.domain.common.queries import QueryResult


class BatchQueryServiceProtocol(Protocol):
    async def get(self, batch_id: UUID) -> BatchReadDTO | None:
        """Получает партию по UUID"""
        ...

    async def list(self, query: ListBatchesQuery) -> QueryResult[BatchReadDTO]:
        """Получает список партий с фильтрацией, пагинацией и сортировкой"""
        ...
