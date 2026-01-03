from datetime import date, datetime
from typing import Protocol
from uuid import UUID

from src.domain.batches import BatchEntity
from src.domain.common.repository_protocol import BaseRepositoryProtocol


class BatchRepositoryProtocol(BaseRepositoryProtocol[BatchEntity], Protocol):
    async def get_by_batch_number_and_date(self, batch_number: int, batch_date: date) -> BatchEntity | None:
        """Находит партию по номеру партии и дате."""
        ...

    async def get_by_work_center(self, work_center_id: UUID) -> list[BatchEntity]:
        """Находит все партии рабочего центра для валидации бизнес-правил."""
        ...

    async def get_expired_open_batches(self, before_time: datetime) -> list[BatchEntity]:
        """Находит открытые партии с shift_end_time < before_time."""
        ...
