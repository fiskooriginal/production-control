from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.common.exceptions import AlreadyExistsError, DoesNotExistError
from src.domain.work_centers.entities import WorkCenterEntity
from src.domain.work_centers.interfaces import WorkCenterRepositoryProtocol
from src.infrastructure.exceptions import DatabaseException
from src.infrastructure.persistence.mappers.work_centers import to_domain_entity, to_persistence_model
from src.infrastructure.persistence.models.work_center import WorkCenter


class WorkCenterRepository(WorkCenterRepositoryProtocol):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_or_raise(self, uuid: UUID) -> WorkCenterEntity:
        """Получает рабочий центр по UUID для write-операций"""
        try:
            work_center_model = await self._session.get(WorkCenter, uuid)
            if work_center_model is None:
                raise DoesNotExistError(f"Рабочий центр с UUID {uuid} не найден")
            return to_domain_entity(work_center_model)
        except DoesNotExistError:
            raise
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении рабочего центра: {e}") from e

    async def create(self, domain_entity: WorkCenterEntity, author: UUID | None = None) -> WorkCenterEntity:
        """Создает новый рабочий центр в репозитории"""
        try:
            stmt = select(WorkCenter.uuid).where(WorkCenter.uuid == domain_entity.uuid)
            result = await self._session.execute(stmt)
            if result.scalar_one_or_none() is not None:
                raise AlreadyExistsError(f"Рабочий центр с UUID {domain_entity.uuid} уже существует")
        except AlreadyExistsError:
            raise
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при проверке существования рабочего центра: {e}") from e

        work_center_model = to_persistence_model(domain_entity, existing_model=None)
        if author is not None:
            work_center_model.author = author

        try:
            self._session.add(work_center_model)
            await self._session.flush()
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при создании рабочего центра: {e}") from e

        return to_domain_entity(work_center_model)

    async def update(self, domain_entity: WorkCenterEntity) -> WorkCenterEntity:
        """Обновляет существующий рабочий центр"""
        work_center_model = await self._session.get(WorkCenter, domain_entity.uuid)
        if work_center_model is None:
            raise DoesNotExistError(f"Рабочий центр с UUID {domain_entity.uuid} не найден")
        updated_model = to_persistence_model(domain_entity, existing_model=work_center_model)
        for key, value in updated_model.model_dump(exclude={"uuid", "created_at"}).items():
            setattr(work_center_model, key, value)

        try:
            await self._session.flush()
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при обновлении рабочего центра: {e}") from e

        return to_domain_entity(work_center_model)

    async def delete(self, uuid: UUID) -> None:
        """Удаляет рабочий центр по UUID"""
        try:
            work_center_model = await self._session.get(WorkCenter, uuid)
            if work_center_model is None:
                raise DoesNotExistError(f"Рабочий центр с UUID {uuid} не найден")
            await self._session.delete(work_center_model)
        except DoesNotExistError:
            raise
        except Exception as e:
            raise DatabaseException(f"Ошибка при удалении рабочего центра: {e}") from e

    async def get_by_identifier(self, identifier: str) -> WorkCenterEntity | None:
        """Находит рабочий центр по идентификатору"""
        try:
            stmt = select(WorkCenter).where(WorkCenter.identifier == identifier)
            result = await self._session.execute(stmt)
            work_center_model = result.scalar_one_or_none()
            if work_center_model is None:
                return None
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при поиске рабочего центра по идентификатору: {e}") from e

        return to_domain_entity(work_center_model)
