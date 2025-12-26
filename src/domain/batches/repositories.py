from typing import Protocol

from src.domain.batches.entities import BatchEntity
from src.domain.shared.repository_protocol import BaseRepositoryProtocol


class BatchRepositoryProtocol(BaseRepositoryProtocol[BatchEntity], Protocol):
    async def get_by_batch_number(self, batch_number: int) -> BatchEntity | None:
        """Находит партию по номеру партии."""
        ...
