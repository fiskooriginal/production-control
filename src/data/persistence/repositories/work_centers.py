from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.mappers.work_centers import to_domain_entity, to_persistence_model
from src.data.persistence.models.work_center import WorkCenter
from src.domain.shared.exceptions import AlreadyExistsError, DoesNotExistError
from src.domain.shared.queries import PaginationSpec, QueryResult, SortSpec
from src.domain.work_centers.entities import WorkCenterEntity
from src.domain.work_centers.repositories import WorkCenterRepositoryProtocol


class WorkCenterRepository(WorkCenterRepositoryProtocol):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, entity: WorkCenterEntity, author: UUID | None = None) -> WorkCenterEntity:
        """Создает новый рабочий центр в репозитории"""
        existing = await self.get(entity.uuid)
        if existing is not None:
            raise AlreadyExistsError(f"Рабочий центр с UUID {entity.uuid} уже существует")
        work_center_model = to_persistence_model(entity, existing_model=None)
        if author is not None:
            work_center_model.author = author
        self._session.add(work_center_model)
        await self._session.flush()
        return to_domain_entity(work_center_model)

    async def get(self, uuid: UUID) -> WorkCenterEntity | None:
        """Получает рабочий центр по UUID"""
        work_center_model = await self._session.get(WorkCenter, uuid)
        if work_center_model is None:
            return None
        return to_domain_entity(work_center_model)

    async def get_or_raise(self, uuid: UUID) -> WorkCenterEntity:
        """Получает рабочий центр по UUID или выбрасывает исключение"""
        work_center = await self.get(uuid)
        if work_center is None:
            raise DoesNotExistError(f"Рабочий центр с UUID {uuid} не найден")
        return work_center

    async def update(self, entity: WorkCenterEntity) -> WorkCenterEntity:
        """Обновляет существующий рабочий центр"""
        work_center_model = await self._session.get(WorkCenter, entity.uuid)
        if work_center_model is None:
            raise DoesNotExistError(f"Рабочий центр с UUID {entity.uuid} не найден")
        updated_model = to_persistence_model(entity, existing_model=work_center_model)
        for key, value in updated_model.model_dump(exclude={"uuid", "created_at"}).items():
            setattr(work_center_model, key, value)
        await self._session.flush()
        return to_domain_entity(work_center_model)

    async def delete(self, uuid: UUID) -> None:
        """Удаляет рабочий центр по UUID"""
        work_center_model = await self._session.get(WorkCenter, uuid)
        if work_center_model is None:
            raise DoesNotExistError(f"Рабочий центр с UUID {uuid} не найден")
        await self._session.delete(work_center_model)

    async def exists(self, uuid: UUID) -> bool:
        """Проверяет существование рабочего центра по UUID"""
        stmt = select(WorkCenter.uuid).where(WorkCenter.uuid == uuid)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def list(
        self,
        pagination: PaginationSpec | None = None,
        sort: SortSpec | None = None,
        filters: dict[str, Any] | None = None,
    ) -> QueryResult[WorkCenterEntity]:
        """Получает список рабочих центров с пагинацией, сортировкой и фильтрацией"""
        stmt = select(WorkCenter)
        if filters and "identifier" in filters and filters["identifier"] is not None:
            stmt = stmt.where(WorkCenter.identifier == filters["identifier"])
        if sort:
            order_by = getattr(WorkCenter, sort.field)
            if sort.direction.value == "desc":
                order_by = order_by.desc()
            stmt = stmt.order_by(order_by)
        count_stmt = select(WorkCenter)
        if filters and "identifier" in filters and filters["identifier"] is not None:
            count_stmt = count_stmt.where(WorkCenter.identifier == filters["identifier"])
        total_result = await self._session.execute(select(func.count()).select_from(count_stmt.subquery()))
        total = total_result.scalar_one() or 0
        if pagination:
            stmt = stmt.offset(pagination.offset).limit(pagination.limit)
        result = await self._session.execute(stmt)
        work_centers = result.scalars().all()
        entities = [to_domain_entity(wc) for wc in work_centers]
        return QueryResult(
            items=entities,
            total=total,
            limit=pagination.limit if pagination else None,
            offset=pagination.offset if pagination else None,
        )

    async def get_by_identifier(self, identifier: str) -> WorkCenterEntity | None:
        """Находит рабочий центр по идентификатору"""
        stmt = select(WorkCenter).where(WorkCenter.identifier == identifier)
        result = await self._session.execute(stmt)
        work_center_model = result.scalar_one_or_none()
        if work_center_model is None:
            return None
        return to_domain_entity(work_center_model)
