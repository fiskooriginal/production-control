from datetime import date, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.time import datetime_aware_to_naive
from src.domain.batches import BatchEntity
from src.domain.batches.interfaces.repository import BatchRepositoryProtocol
from src.domain.common.exceptions import DoesNotExistError
from src.infrastructure.common.exceptions import DatabaseException
from src.infrastructure.persistence.mappers.batches import to_domain_entity, to_persistence_model
from src.infrastructure.persistence.models.batch import Batch
from src.infrastructure.persistence.repositories.base import BaseRepository


class BatchRepository(BaseRepository[BatchEntity, Batch], BatchRepositoryProtocol):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Batch, to_domain_entity, to_persistence_model)

    async def _get_model_or_raise(self, uuid: UUID) -> Batch:
        """Переопределяет метод для использования select() вместо session.get()"""
        try:
            stmt = select(self._model_class).where(self._model_class.uuid == uuid)
            result = await self._session.execute(stmt)
            batch_model = result.scalar_one_or_none()
            if batch_model is None:
                raise DoesNotExistError(f"{self._model_name} с UUID {uuid} не найдена")
            return batch_model
        except DoesNotExistError:
            raise
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении {self._model_name}: {e}") from e

    async def get_by_batch_number_and_date(self, batch_number: int, batch_date: date) -> BatchEntity | None:
        """Находит партию по номеру партии и дате"""
        try:
            stmt = select(self._model_class).where(
                self._model_class.batch_number == batch_number,
                self._model_class.batch_date == batch_date,
            )
            result = await self._session.execute(stmt)
            batch_model = result.scalar_one_or_none()
            if batch_model is None:
                return None
            return self._to_domain_entity(batch_model)
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при поиске партии по номеру и дате: {e}") from e

    async def get_by_work_center(self, work_center_id: UUID) -> list[BatchEntity]:
        """Находит все партии рабочего центра"""
        try:
            stmt = select(self._model_class).where(self._model_class.work_center_id == work_center_id)
            result = await self._session.execute(stmt)
            batch_models = result.scalars().all()
            return [self._to_domain_entity(batch) for batch in batch_models]
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при поиске партий по рабочему центру: {e}") from e

    async def get_expired_open_batches(self, before_time: datetime) -> list[BatchEntity]:
        """Находит открытые партии с shift_end_time < before_time"""
        try:
            before_time_naive = datetime_aware_to_naive(before_time)
            stmt = select(self._model_class).where(
                not self._model_class.is_closed, self._model_class.shift_end_time < before_time_naive
            )
            result = await self._session.execute(stmt)
            batch_models = result.scalars().all()
            return [self._to_domain_entity(batch) for batch in batch_models]
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при поиске просроченных партий: {e}") from e
