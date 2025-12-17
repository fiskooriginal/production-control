from typing import Protocol

from src.domain.repositories.protocol import BaseRepositoryProtocol
from src.domain.work_centers.entities import WorkCenterEntity


class WorkCenterRepositoryProtocol(BaseRepositoryProtocol[WorkCenterEntity], Protocol):
    async def get_by_identifier(self, identifier: str) -> WorkCenterEntity | None:
        """Находит рабочий центр по идентификатору."""
        ...
