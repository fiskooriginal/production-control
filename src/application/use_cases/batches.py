from uuid import UUID

from src.application.dtos.batches import CloseBatchInputDTO, CreateBatchInputDTO
from src.application.mappers.batches import input_dto_to_entity
from src.application.uow import UnitOfWorkProtocol
from src.core.logging import get_logger
from src.domain.batches.entities import BatchEntity
from src.domain.batches.events import BatchCreatedEvent
from src.domain.batches.services import validate_batch_number_uniqueness, validate_shift_time_overlap
from src.domain.common.exceptions import InvalidStateError
from src.domain.products.entities import ProductEntity
from src.domain.products.value_objects import ProductCode

logger = get_logger("use_case.batches")


class CreateBatchUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, input_dto: CreateBatchInputDTO) -> BatchEntity:
        """Создает новую партию с автоматическим сохранением доменных событий в outbox"""
        logger.info(f"Creating batch: batch_number={input_dto.batch_number}")
        try:
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

                result = await self._uow.batches.create(batch_entity)
                logger.info(f"Batch created successfully: batch_id={result.uuid}")
                return result
        except Exception as e:
            logger.exception(f"Failed to create batch: {e}")
            raise


class CloseBatchUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, input_dto: CloseBatchInputDTO) -> BatchEntity:
        """Закрывает партию с автоматическим сохранением доменных событий в outbox"""
        logger.info(f"Closing batch: batch_id={input_dto.batch_id}")
        try:
            async with self._uow:
                batch = await self._uow.batches.get_or_raise(input_dto.batch_id)
                if not batch.can_close():
                    raise InvalidStateError("Не все продукты в партии агрегированы")
                batch.close(input_dto.closed_at)
                result = await self._uow.batches.update(batch)
                logger.info(f"Batch closed successfully: batch_id={input_dto.batch_id}")
                return result
        except Exception as e:
            logger.exception(f"Failed to close batch: {e}")
            raise


class AddProductToBatchUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, batch_id: UUID, unique_code: str) -> BatchEntity:
        """Добавляет продукт в партию с автоматическим сохранением доменных событий в outbox"""
        logger.info(f"Adding product to batch: batch_id={batch_id} unique_code={unique_code}")
        try:
            async with self._uow:
                batch = await self._uow.batches.get_or_raise(batch_id)

                if batch.is_closed:
                    raise InvalidStateError("Нельзя добавлять продукты в закрытую партию")

                product = ProductEntity(unique_code=ProductCode(unique_code), batch_id=batch_id)

                await self._uow.products.create(product)
                batch.add_product(product)
                await self._uow.batches.update(batch)
                logger.info(f"Product added to batch successfully: product_id={product.uuid}")
                return batch
        except Exception as e:
            logger.exception(f"Failed to add product to batch: {e}")
            raise


class RemoveProductFromBatchUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, batch_id: UUID, product_id: UUID) -> BatchEntity:
        """Удаляет продукт из партии с автоматическим сохранением доменных событий в outbox"""
        logger.info(f"Removing product from batch: batch_id={batch_id} product_id={product_id}")
        try:
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

                await self._uow.products.delete(product_id)
                batch.remove_product(product)
                await self._uow.batches.update(batch)
                logger.info(f"Product removed from batch successfully: product_id={product_id}")
                return batch
        except Exception as e:
            logger.exception(f"Failed to remove product from batch: {e}")
            raise
