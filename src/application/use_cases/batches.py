from datetime import date, datetime
from uuid import UUID

from src.application.dtos.batches import BatchFilters
from src.application.uow import UnitOfWorkProtocol
from src.data.persistence.repositories.batches import BatchRepository
from src.data.persistence.repositories.products import ProductRepository
from src.domain.batches.entities import BatchEntity
from src.domain.batches.events import BatchCreatedEvent
from src.domain.batches.services import can_close_batch, validate_batch_number_uniqueness, validate_shift_time_overlap
from src.domain.batches.value_objects import (
    BatchNumber,
    EknCode,
    Nomenclature,
    Shift,
    ShiftTimeRange,
    TaskDescription,
    Team,
)
from src.domain.products.entities import ProductEntity
from src.domain.shared.exceptions import InvalidStateError
from src.domain.shared.queries import PaginationSpec, QueryResult, SortSpec


class CreateBatchUseCase:
    """
    Use case для создания партии.
    Использует UnitOfWork для атомарного сохранения партии и доменных событий.
    """

    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(
        self,
        task_description: str,
        shift: str,
        team: str,
        batch_number: int,
        batch_date: date,
        nomenclature: str,
        ekn_code: str,
        shift_start: datetime,
        shift_end: datetime,
        work_center_id: UUID,
    ) -> BatchEntity:
        """Создает новую партию с автоматическим сохранением доменных событий в outbox"""
        async with self._uow:
            batch_number_vo = BatchNumber(batch_number)
            is_unique = await validate_batch_number_uniqueness(batch_number_vo, self._uow.batches)
            if not is_unique:
                raise InvalidStateError(f"Партия с номером {batch_number} уже существует")

            await self._uow.work_centers.get_or_raise(work_center_id)

            batch_entity = BatchEntity(
                task_description=TaskDescription(task_description),
                shift=Shift(shift),
                team=Team(team),
                batch_number=batch_number_vo,
                batch_date=batch_date,
                nomenclature=Nomenclature(nomenclature),
                ekn_code=EknCode(ekn_code),
                shift_time_range=ShiftTimeRange(start=shift_start, end=shift_end),
                products=[],
                work_center_id=work_center_id,
            )

            is_valid = await validate_shift_time_overlap(batch_entity, self._uow.batches)
            if not is_valid:
                raise InvalidStateError("Время смены пересекается с другой партией")

            batch_entity.add_domain_event(
                BatchCreatedEvent(
                    aggregate_id=batch_entity.uuid,
                    batch_number=batch_number_vo,
                    batch_date=batch_date,
                    work_center_id=work_center_id,
                )
            )

            result = await self._uow.batches.create(batch_entity)
            return result


class CloseBatchUseCase:
    """
    Use case для закрытия партии.
    Использует UnitOfWork для атомарного обновления партии и сохранения доменных событий.
    """

    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, batch_id: UUID, closed_at: datetime | None = None) -> BatchEntity:
        """Закрывает партию с автоматическим сохранением доменных событий в outbox"""
        async with self._uow:
            batch = await self._uow.batches.get_or_raise(batch_id)
            if not can_close_batch(batch):
                raise InvalidStateError("Не все продукты в партии агрегированы")
            batch.close(closed_at)
            result = await self._uow.batches.update(batch)
            return result


class AddProductToBatchUseCase:
    def __init__(
        self,
        batch_repository: BatchRepository,
        product_repository: ProductRepository,
    ):
        self._batch_repository = batch_repository
        self._product_repository = product_repository

    async def execute(self, batch_id: UUID, product: ProductEntity) -> BatchEntity:
        """Добавляет продукт в партию"""
        batch = await self._batch_repository.get_or_raise(batch_id)
        if product.batch_id != batch_id:
            from dataclasses import replace

            product = replace(product, batch_id=batch_id)
        batch.add_product(product)
        await self._product_repository.create(product)
        return await self._batch_repository.update(batch)


class ListBatchesUseCase:
    def __init__(self, batch_repository: BatchRepository):
        self._batch_repository = batch_repository

    async def execute(
        self,
        filters: BatchFilters | None = None,
        pagination: PaginationSpec | None = None,
        sort: SortSpec | None = None,
    ) -> QueryResult[BatchEntity]:
        """Получает список партий"""
        return await self._batch_repository.list(filters=filters, pagination=pagination, sort=sort)
