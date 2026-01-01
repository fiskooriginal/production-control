from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.batches.entities import BatchEntity
from src.domain.batches.interfaces.repository import BatchRepositoryProtocol
from src.domain.common.exceptions import AlreadyExistsError, DoesNotExistError
from src.infrastructure.common.exceptions import DatabaseException
from src.infrastructure.persistence.mappers.batches import to_domain_entity, to_persistence_model
from src.infrastructure.persistence.models.batch import Batch


class BatchRepository(BatchRepositoryProtocol):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def _get_or_raise(self, uuid: UUID) -> Batch:
        try:
            stmt = select(Batch).where(Batch.uuid == uuid)
            result = await self._session.execute(stmt)
            batch_model = result.scalar_one_or_none()
            if batch_model is None:
                raise DoesNotExistError(f"Партия с UUID {uuid} не найдена")
            return batch_model
        except DoesNotExistError:
            raise
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении партии: {e}") from e

    async def get_or_raise(self, uuid: UUID) -> BatchEntity:
        """Получает партию по UUID для write-операций"""
        batch_model = await self._get_or_raise(uuid)
        return to_domain_entity(batch_model)

    async def create(self, domain_entity: BatchEntity) -> BatchEntity:
        """Создает новую партию в репозитории"""
        try:
            stmt = select(Batch.uuid).where(Batch.uuid == domain_entity.uuid)
            result = await self._session.execute(stmt)
            if result.scalar_one_or_none() is not None:
                raise AlreadyExistsError(f"Партия с UUID {domain_entity.uuid} уже существует")
        except AlreadyExistsError:
            raise
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при проверке существования партии: {e}") from e

        batch_model = to_persistence_model(domain_entity)
        try:
            self._session.add(batch_model)
            await self._session.flush()
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при создании партии: {e}") from e

        return to_domain_entity(batch_model)

    async def update(self, domain_entity: BatchEntity) -> BatchEntity:
        """Обновляет существующую партию"""
        batch_model = await self._get_or_raise(domain_entity.uuid)
        updated_model = to_persistence_model(domain_entity)
        for key, value in updated_model.model_dump(exclude={"uuid", "created_at"}).items():
            setattr(batch_model, key, value)

        try:
            await self._session.flush()
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при обновлении партии: {e}") from e

        return to_domain_entity(batch_model)

    async def delete(self, uuid: UUID) -> None:
        """Удаляет партию по UUID"""
        try:
            batch_model = await self._get_or_raise(uuid)
            await self._session.delete(batch_model)
        except DoesNotExistError:
            raise
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при удалении партии: {e}") from e

    async def get_by_batch_number(self, batch_number: int) -> BatchEntity | None:
        """Находит партию по номеру партии"""
        try:
            stmt = select(Batch).where(Batch.batch_number == batch_number)
            result = await self._session.execute(stmt)
            batch_model = result.scalar_one_or_none()
            if batch_model is None:
                return None
            return to_domain_entity(batch_model)
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при поиске партии по номеру: {e}") from e

    async def get_by_work_center(self, work_center_id: UUID) -> list[BatchEntity]:
        """Находит все партии рабочего центра"""
        try:
            stmt = select(Batch).where(Batch.work_center_id == work_center_id)
            result = await self._session.execute(stmt)
            batch_models = result.scalars().all()
            return [to_domain_entity(batch) for batch in batch_models]
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при поиске партий по рабочему центру: {e}") from e
