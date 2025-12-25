from uuid import UUID

from src.application.dtos.work_centers import CreateWorkCenterInputDTO, UpdateWorkCenterInputDTO, WorkCenterFilters
from src.application.mappers.work_centers import input_dto_to_entity, update_dto_to_entity
from src.application.uow import UnitOfWorkProtocol
from src.domain.shared.exceptions import InvalidStateError
from src.domain.shared.queries import PaginationSpec, QueryResult, SortSpec
from src.domain.work_centers.entities import WorkCenterEntity


class CreateWorkCenterUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, input_dto: CreateWorkCenterInputDTO) -> WorkCenterEntity:
        """Создает новый рабочий центр"""
        async with self._uow:
            # Валидация уникальности identifier
            existing = await self._uow.work_centers.get_by_identifier(input_dto.identifier)
            if existing is not None:
                raise InvalidStateError(f"Рабочий центр с идентификатором {input_dto.identifier} уже существует")

            # Создание domain_entity через маппер
            work_center_entity = input_dto_to_entity(input_dto)

            # Сохранение через репозиторий
            return await self._uow.work_centers.create(work_center_entity)


class GetWorkCenterUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, work_center_id: UUID) -> WorkCenterEntity:
        """Получает рабочий центр по UUID"""
        async with self._uow:
            return await self._uow.work_centers.get_or_raise(work_center_id)


class UpdateWorkCenterUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, input_dto: UpdateWorkCenterInputDTO) -> WorkCenterEntity:
        """Обновляет рабочий центр"""
        async with self._uow:
            # Загружаем domain_entity
            work_center = await self._uow.work_centers.get_or_raise(input_dto.work_center_id)

            # Если обновляется identifier, проверяем уникальность
            if input_dto.identifier is not None and input_dto.identifier != work_center.identifier.value:
                existing = await self._uow.work_centers.get_by_identifier(input_dto.identifier)
                if existing is not None:
                    raise InvalidStateError(f"Рабочий центр с идентификатором {input_dto.identifier} уже существует")

            # Обновляем поля
            updated_entity = update_dto_to_entity(work_center, input_dto)

            # Сохраняем
            return await self._uow.work_centers.update(updated_entity)


class DeleteWorkCenterUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, work_center_id: UUID) -> None:
        """Удаляет рабочий центр"""
        async with self._uow:
            # Проверяем существование
            await self._uow.work_centers.get_or_raise(work_center_id)
            # Удаляем
            await self._uow.work_centers.delete(work_center_id)


class ListWorkCentersUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(
        self,
        filters: WorkCenterFilters | None = None,
        pagination: PaginationSpec | None = None,
        sort: SortSpec | None = None,
    ) -> QueryResult[WorkCenterEntity]:
        """Получает список рабочих центров с фильтрацией, пагинацией и сортировкой"""
        async with self._uow:
            # Конвертируем WorkCenterFilters в dict для передачи в репозиторий
            filter_dict = None
            if filters:
                filter_dict = {}
                if filters.identifier is not None:
                    filter_dict["identifier"] = filters.identifier
            return await self._uow.work_centers.list(filters=filter_dict, pagination=pagination, sort=sort)
