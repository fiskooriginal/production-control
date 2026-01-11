from collections.abc import Callable
from typing import TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.common.exceptions import AlreadyExistsError, DoesNotExistError
from src.domain.common.repository_protocol import BaseRepositoryProtocol
from src.infrastructure.common.exceptions import DatabaseException

DomainEntity = TypeVar("DomainEntity")
PersistenceModel = TypeVar("PersistenceModel")


class BaseRepository[DomainEntity, PersistenceModel](BaseRepositoryProtocol[DomainEntity]):
    """
    Базовый класс репозитория с общей логикой CRUD операций.

    Типы:
    - DomainEntity: доменная сущность (например, BatchEntity)
    - PersistenceModel: модель БД (например, Batch)
    """

    def __init__(
        self,
        session: AsyncSession,
        model_class: type[PersistenceModel],
        to_domain_entity: Callable[[PersistenceModel], DomainEntity],
        to_persistence_model: Callable[[DomainEntity], PersistenceModel],
    ):
        self._session = session
        self._model_class = model_class
        self._to_domain_entity = to_domain_entity
        self._to_persistence_model = to_persistence_model

        self._model_name = self._model_class.__name__

    async def _get_model_or_raise(self, uuid: UUID) -> PersistenceModel:
        """Внутренний метод для получения модели БД по UUID"""
        try:
            model = await self._session.get(self._model_class, uuid)
            if model is None:
                raise DoesNotExistError(f"{self._model_name} с UUID {uuid} не найден")
            return model
        except DoesNotExistError:
            raise
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении {self._model_name}: {e}") from e

    async def get_or_raise(self, uuid: UUID) -> DomainEntity:
        """Получает доменную сущность по UUID для write-операций"""
        model = await self._get_model_or_raise(uuid)
        return self._to_domain_entity(model)

    async def create(self, domain_entity: DomainEntity) -> DomainEntity:
        """Создает новую доменную сущность"""
        try:
            stmt = select(self._model_class.uuid).where(self._model_class.uuid == domain_entity.uuid)
            result = await self._session.execute(stmt)
            if result.scalar_one_or_none() is not None:
                raise AlreadyExistsError(f"{self._model_name} с UUID {domain_entity.uuid} уже существует")
        except AlreadyExistsError:
            raise
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при проверке существования {self._model_name}: {e}") from e

        persistence_model = self._to_persistence_model(domain_entity)

        try:
            self._session.add(persistence_model)
            await self._session.flush()
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при создании {self._model_name}: {e}") from e

        return self._to_domain_entity(persistence_model)

    async def update(self, domain_entity: DomainEntity) -> DomainEntity:
        """Обновляет существующую доменную сущность"""
        persistence_model = await self._get_model_or_raise(domain_entity.uuid)
        updated_model = self._to_persistence_model(domain_entity)

        for key, value in updated_model.model_dump(exclude={"uuid", "created_at"}).items():
            setattr(persistence_model, key, value)

        try:
            await self._session.flush()
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при обновлении {self._model_name}: {e}") from e

        return self._to_domain_entity(persistence_model)

    async def delete(self, uuid: UUID) -> None:
        """Удаляет сущность по UUID"""
        try:
            persistence_model = await self._get_model_or_raise(uuid)
            await self._session.delete(persistence_model)
        except DoesNotExistError:
            raise
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при удалении {self._model_name}: {e}") from e
