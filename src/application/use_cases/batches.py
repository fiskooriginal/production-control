from uuid import UUID

from src.application.dtos.batches import BatchFilters, CloseBatchInputDTO, CreateBatchInputDTO
from src.application.mappers.batches import input_dto_to_entity
from src.application.uow import UnitOfWorkProtocol
from src.domain.batches.entities import BatchEntity
from src.domain.batches.events import BatchCreatedEvent
from src.domain.batches.services import can_close_batch, validate_batch_number_uniqueness, validate_shift_time_overlap
from src.domain.products.entities import ProductEntity
from src.domain.products.value_objects import ProductCode
from src.domain.shared.exceptions import InvalidStateError
from src.domain.shared.queries import PaginationSpec, QueryResult, SortSpec


class CreateBatchUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, input_dto: CreateBatchInputDTO) -> BatchEntity:
        """Создает новую партию с автоматическим сохранением доменных событий в outbox"""
        async with self._uow:
            # Конвертация DTO → Domain Entity через маппер
            batch_entity = input_dto_to_entity(input_dto)

            # Domain Service валидирует уникальность
            is_unique = await validate_batch_number_uniqueness(batch_entity.batch_number, self._uow.batches)
            if not is_unique:
                raise InvalidStateError(f"Партия с номером {batch_entity.batch_number.value} уже существует")

            # Domain Service проверяет существование work_center
            await self._uow.work_centers.get_or_raise(batch_entity.work_center_id)

            # Domain Service валидирует пересечение времени смены
            is_valid = await validate_shift_time_overlap(batch_entity, self._uow.batches)
            if not is_valid:
                raise InvalidStateError("Время смены пересекается с другой партией")

            # Domain Event
            batch_entity.add_domain_event(
                BatchCreatedEvent(
                    aggregate_id=batch_entity.uuid,
                    batch_number=batch_entity.batch_number,
                    batch_date=batch_entity.batch_date,
                    work_center_id=batch_entity.work_center_id,
                )
            )

            return await self._uow.batches.create(batch_entity)


class CloseBatchUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, input_dto: CloseBatchInputDTO) -> BatchEntity:
        """Закрывает партию с автоматическим сохранением доменных событий в outbox"""
        async with self._uow:
            batch = await self._uow.batches.get_or_raise(input_dto.batch_id)
            if not can_close_batch(batch):
                raise InvalidStateError("Не все продукты в партии агрегированы")
            batch.close(input_dto.closed_at)
            return await self._uow.batches.update(batch)


class AddProductToBatchUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, batch_id: UUID, unique_code: str) -> BatchEntity:
        """Добавляет продукт в партию с автоматическим сохранением доменных событий в outbox"""
        async with self._uow:
            batch = await self._uow.batches.get_or_raise(batch_id)

            product = ProductEntity(
                unique_code=ProductCode(unique_code),
                batch_id=batch_id,
            )

            saved_product = await self._uow.products.create(product)
            batch.add_product(saved_product)

            return await self._uow.batches.update(batch)


class RemoveProductFromBatchUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, batch_id: UUID, product_id: UUID) -> BatchEntity:
        """Удаляет продукт из партии с автоматическим сохранением доменных событий в outbox"""
        async with self._uow:
            # Загружаем партию
            batch = await self._uow.batches.get_or_raise(batch_id)

            # Проверяем, что партия открыта
            if batch.is_closed:
                raise InvalidStateError("Нельзя удалять продукты из закрытой партии")

            # Проверяем, что продукт существует
            product = await self._uow.products.get_or_raise(product_id)

            # Проверяем, что продукт принадлежит этой партии
            if product.batch_id != batch_id:
                raise InvalidStateError("Продукт не принадлежит этой партии")

            # Удаляем ID продукта из партии (генерирует domain event)
            batch.remove_product_id(product_id)

            # Удаляем продукт из БД (так как batch_id не может быть NULL)
            await self._uow.products.delete(product_id)

            # Обновляем партию
            await self._uow.batches.update(batch)

            return batch


class ListBatchesUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(
        self,
        filters: BatchFilters | None = None,
        pagination: PaginationSpec | None = None,
        sort: SortSpec | None = None,
    ) -> QueryResult[BatchEntity]:
        """Получает список партий с фильтрацией, пагинацией и сортировкой"""
        async with self._uow:
            # Конвертируем BatchFilters в dict для передачи в репозиторий
            filter_dict = None
            if filters:
                filter_dict = {}
                if filters.is_closed is not None:
                    filter_dict["is_closed"] = filters.is_closed
                if filters.batch_number is not None:
                    filter_dict["batch_number"] = filters.batch_number
                if filters.batch_date is not None:
                    filter_dict["batch_date"] = filters.batch_date
                if filters.work_center_id is not None:
                    filter_dict["work_center_id"] = filters.work_center_id
                if filters.shift is not None:
                    filter_dict["shift"] = filters.shift
            return await self._uow.batches.list(filters=filter_dict, pagination=pagination, sort=sort)
