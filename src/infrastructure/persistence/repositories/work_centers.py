from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.work_centers import WorkCenterEntity
from src.domain.work_centers.interfaces import WorkCenterRepositoryProtocol
from src.infrastructure.common.exceptions import DatabaseException
from src.infrastructure.persistence.mappers.work_centers import to_domain_entity, to_persistence_model
from src.infrastructure.persistence.models.work_center import WorkCenter
from src.infrastructure.persistence.repositories.base import BaseRepository


class WorkCenterRepository(BaseRepository[WorkCenterEntity, WorkCenter], WorkCenterRepositoryProtocol):
    def __init__(self, session: AsyncSession):
        super().__init__(session, WorkCenter, to_domain_entity, to_persistence_model)

    async def get_by_identifier(self, identifier: str) -> WorkCenterEntity | None:
        """Находит рабочий центр по идентификатору"""
        try:
            stmt = select(self._model_class).where(self._model_class.identifier == identifier)
            result = await self._session.execute(stmt)
            work_center_model = result.scalar_one_or_none()
            if work_center_model is None:
                return None
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при поиске рабочего центра по идентификатору: {e}") from e

        return self._to_domain_entity(work_center_model)
