from typing import Protocol
from uuid import UUID

from src.domain.batches.entities import BatchEntity
from src.domain.common.repository_protocol import BaseRepositoryProtocol


class BatchRepositoryProtocol(BaseRepositoryProtocol[BatchEntity], Protocol):
    async def get_by_batch_number(self, batch_number: int) -> BatchEntity | None:
        """Находит партию по номеру партии."""
        ...

    async def get_by_work_center(self, work_center_id: UUID) -> list[BatchEntity]:
        """Находит все партии рабочего центра для валидации бизнес-правил."""
        ...
