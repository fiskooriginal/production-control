from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError, IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.batches.entities import BatchEntity
from src.domain.batches.repositories import BatchRepositoryProtocol
from src.domain.shared.exceptions import AlreadyExistsError, DoesNotExistError
from src.domain.shared.queries import PaginationSpec, QueryResult, SortSpec
from src.infrastructure.exceptions import DatabaseException, MappingException
from src.infrastructure.persistence.mappers.batches import to_domain_entity, to_persistence_model
from src.infrastructure.persistence.models.batch import Batch


class BatchRepository(BatchRepositoryProtocol):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, domain_entity: BatchEntity) -> BatchEntity:
        """Создает новую партию в репозитории"""
        try:
            existing = await self.get(domain_entity.uuid)
            if existing is not None:
                raise AlreadyExistsError(f"Партия с UUID {domain_entity.uuid} уже существует")
            batch_model = to_persistence_model(domain_entity)
            self._session.add(batch_model)
            await self._session.flush()
            return to_domain_entity(batch_model)
        except (AlreadyExistsError, DoesNotExistError):
            raise
        except IntegrityError as e:
            raise DatabaseException(f"Ошибка целостности данных при создании партии: {e}") from e
        except DBAPIError as e:
            raise DatabaseException(f"Ошибка базы данных при создании партии: {e}") from e
        except SQLAlchemyError as e:
            raise DatabaseException(f"Ошибка SQLAlchemy при создании партии: {e}") from e
        except Exception as e:
            raise MappingException(f"Ошибка маппинга при создании партии: {e}") from e

    async def get(self, uuid: UUID) -> BatchEntity | None:
        """Получает партию по UUID"""
        try:
            stmt = select(Batch).where(Batch.uuid == uuid)
            result = await self._session.execute(stmt)
            batch_model = result.scalar_one_or_none()
            if batch_model is None:
                return None
            return to_domain_entity(batch_model)
        except DBAPIError as e:
            raise DatabaseException(f"Ошибка базы данных при получении партии: {e}") from e
        except SQLAlchemyError as e:
            raise DatabaseException(f"Ошибка SQLAlchemy при получении партии: {e}") from e
        except Exception as e:
            raise MappingException(f"Ошибка маппинга при получении партии: {e}") from e

    async def get_or_raise(self, uuid: UUID) -> BatchEntity:
        """Получает партию по UUID или выбрасывает исключение"""
        batch = await self.get(uuid)
        if batch is None:
            raise DoesNotExistError(f"Партия с UUID {uuid} не найдена")
        return batch

    async def update(self, domain_entity: BatchEntity) -> BatchEntity:
        """Обновляет существующую партию"""
        try:
            batch_model = await self._session.get(Batch, domain_entity.uuid)
            if batch_model is None:
                raise DoesNotExistError(f"Партия с UUID {domain_entity.uuid} не найдена")
            updated_model = to_persistence_model(domain_entity)
            for key, value in updated_model.model_dump(exclude={"uuid", "created_at"}).items():
                setattr(batch_model, key, value)
            await self._session.flush()
            return to_domain_entity(batch_model)
        except (AlreadyExistsError, DoesNotExistError):
            raise
        except IntegrityError as e:
            raise DatabaseException(f"Ошибка целостности данных при обновлении партии: {e}") from e
        except DBAPIError as e:
            raise DatabaseException(f"Ошибка базы данных при обновлении партии: {e}") from e
        except SQLAlchemyError as e:
            raise DatabaseException(f"Ошибка SQLAlchemy при обновлении партии: {e}") from e
        except Exception as e:
            raise MappingException(f"Ошибка маппинга при обновлении партии: {e}") from e

    async def delete(self, uuid: UUID) -> None:
        """Удаляет партию по UUID"""
        try:
            batch_model = await self._session.get(Batch, uuid)
            if batch_model is None:
                raise DoesNotExistError(f"Партия с UUID {uuid} не найдена")
            await self._session.delete(batch_model)
        except (AlreadyExistsError, DoesNotExistError):
            raise
        except IntegrityError as e:
            raise DatabaseException(f"Ошибка целостности данных при удалении партии: {e}") from e
        except DBAPIError as e:
            raise DatabaseException(f"Ошибка базы данных при удалении партии: {e}") from e
        except SQLAlchemyError as e:
            raise DatabaseException(f"Ошибка SQLAlchemy при удалении партии: {e}") from e

    async def exists(self, uuid: UUID) -> bool:
        """Проверяет существование партии по UUID"""
        try:
            stmt = select(Batch.uuid).where(Batch.uuid == uuid)
            result = await self._session.execute(stmt)
            return result.scalar_one_or_none() is not None
        except DBAPIError as e:
            raise DatabaseException(f"Ошибка базы данных при проверке существования партии: {e}") from e
        except SQLAlchemyError as e:
            raise DatabaseException(f"Ошибка SQLAlchemy при проверке существования партии: {e}") from e

    async def _list_base(
        self,
        pagination: PaginationSpec | None = None,
        sort: SortSpec | None = None,
        filters: dict[str, Any] | None = None,
    ) -> QueryResult[BatchEntity]:
        """Базовый метод для получения списка партий"""
        try:
            stmt = select(Batch)
            if filters:
                if "is_closed" in filters and filters["is_closed"] is not None:
                    stmt = stmt.where(Batch.is_closed == filters["is_closed"])
                if "batch_number" in filters and filters["batch_number"] is not None:
                    stmt = stmt.where(Batch.batch_number == filters["batch_number"])
                if "batch_date" in filters and filters["batch_date"] is not None:
                    stmt = stmt.where(Batch.batch_date == filters["batch_date"])
                if "work_center_id" in filters and filters["work_center_id"] is not None:
                    stmt = stmt.where(Batch.work_center_id == filters["work_center_id"])
                if "shift" in filters and filters["shift"] is not None:
                    stmt = stmt.where(Batch.shift == filters["shift"])
            if sort:
                order_by = getattr(Batch, sort.field)
                if sort.direction.value == "desc":
                    order_by = order_by.desc()
                stmt = stmt.order_by(order_by)
            count_stmt = select(Batch)
            if filters:
                if "is_closed" in filters and filters["is_closed"] is not None:
                    count_stmt = count_stmt.where(Batch.is_closed == filters["is_closed"])
                if "batch_number" in filters and filters["batch_number"] is not None:
                    count_stmt = count_stmt.where(Batch.batch_number == filters["batch_number"])
                if "batch_date" in filters and filters["batch_date"] is not None:
                    count_stmt = count_stmt.where(Batch.batch_date == filters["batch_date"])
                if "work_center_id" in filters and filters["work_center_id"] is not None:
                    count_stmt = count_stmt.where(Batch.work_center_id == filters["work_center_id"])
                if "shift" in filters and filters["shift"] is not None:
                    count_stmt = count_stmt.where(Batch.shift == filters["shift"])
            total_result = await self._session.execute(select(func.count()).select_from(count_stmt.subquery()))
            total = total_result.scalar_one() or 0
            if pagination:
                stmt = stmt.offset(pagination.offset).limit(pagination.limit)
            result = await self._session.execute(stmt)
            batches = result.scalars().all()
            entities = [to_domain_entity(b) for b in batches]
            return QueryResult(
                items=entities,
                total=total,
                limit=pagination.limit if pagination else None,
                offset=pagination.offset if pagination else None,
            )
        except DBAPIError as e:
            raise DatabaseException(f"Ошибка базы данных при получении списка партий: {e}") from e
        except SQLAlchemyError as e:
            raise DatabaseException(f"Ошибка SQLAlchemy при получении списка партий: {e}") from e
        except Exception as e:
            raise MappingException(f"Ошибка маппинга при получении списка партий: {e}") from e

    async def get_by_batch_number(self, batch_number: int) -> BatchEntity | None:
        """Находит партию по номеру партии"""
        try:
            stmt = select(Batch).where(Batch.batch_number == batch_number)
            result = await self._session.execute(stmt)
            batch_model = result.scalar_one_or_none()
            if batch_model is None:
                return None
            return to_domain_entity(batch_model)
        except DBAPIError as e:
            raise DatabaseException(f"Ошибка базы данных при поиске партии по номеру: {e}") from e
        except SQLAlchemyError as e:
            raise DatabaseException(f"Ошибка SQLAlchemy при поиске партии по номеру: {e}") from e
        except Exception as e:
            raise MappingException(f"Ошибка маппинга при поиске партии по номеру: {e}") from e

    async def get_by_work_center(self, work_center_uuid: UUID) -> list[BatchEntity]:
        """Находит все партии для указанного рабочего центра"""
        try:
            stmt = select(Batch).where(Batch.work_center_id == work_center_uuid)
            result = await self._session.execute(stmt)
            batches = result.scalars().all()
            return [to_domain_entity(b) for b in batches]
        except DBAPIError as e:
            raise DatabaseException(f"Ошибка базы данных при поиске партий по рабочему центру: {e}") from e
        except SQLAlchemyError as e:
            raise DatabaseException(f"Ошибка SQLAlchemy при поиске партий по рабочему центру: {e}") from e
        except Exception as e:
            raise MappingException(f"Ошибка маппинга при поиске партий по рабочему центру: {e}") from e

    async def list(
        self,
        filters: dict[str, Any] | None = None,
        pagination: PaginationSpec | None = None,
        sort: SortSpec | None = None,
    ) -> QueryResult[BatchEntity]:
        """Получает список партий с фильтрацией, пагинацией и сортировкой"""
        return await self._list_base(pagination=pagination, sort=sort, filters=filters)
