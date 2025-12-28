from uuid import UUID

from src.application.batches.dtos import CreateBatchInputDTO
from src.application.batches.mappers import create_input_dto_to_entity
from src.application.common.uow import UnitOfWorkProtocol
from src.core.logging import get_logger
from src.domain.batches.entities import BatchEntity
from src.domain.batches.events import BatchCreatedEvent
from src.domain.batches.services import validate_batch_number_uniqueness, validate_shift_time_overlap
from src.domain.common.exceptions import InvalidStateError
from src.infrastructure.cache.keys import get_batch_key, get_batches_list_pattern
from src.infrastructure.cache.protocol import CacheServiceProtocol

logger = get_logger("command.batches")


class CreateBatchCommand:
    def __init__(self, uow: UnitOfWorkProtocol, cache_service: CacheServiceProtocol | None = None):
        self._uow = uow
        self._cache_service = cache_service

    async def execute(self, input_dto: CreateBatchInputDTO) -> BatchEntity:
        """Создает новую партию с автоматическим сохранением доменных событий в outbox"""
        logger.info(f"Creating batch: batch_number={input_dto.batch_number}")
        batch_id = None
        try:
            async with self._uow:
                batch_entity = create_input_dto_to_entity(input_dto)

                is_unique = await validate_batch_number_uniqueness(batch_entity.batch_number, self._uow.batches)
                if not is_unique:
                    raise InvalidStateError(f"Партия с номером {batch_entity.batch_number.value} уже существует")

                await self._uow.work_centers.get_or_raise(batch_entity.work_center_id)

                is_valid = await validate_shift_time_overlap(batch_entity, self._uow.batches)
                if not is_valid:
                    raise InvalidStateError("Время смены пересекается с другой партией")

                batch_entity.add_domain_event(
                    BatchCreatedEvent(
                        aggregate_id=batch_entity.uuid,
                        batch_number=batch_entity.batch_number,
                        batch_date=batch_entity.batch_date,
                        work_center_id=batch_entity.work_center_id,
                    )
                )

                result = await self._uow.batches.create(batch_entity)
                batch_id = result.uuid
                logger.info(f"Batch created successfully: batch_id={batch_id}")

            if batch_id:
                await self._invalidate_batch_cache(batch_id)
            return result
        except Exception as e:
            logger.exception(f"Failed to create batch: {e}")
            raise

    async def _invalidate_batch_cache(self, batch_id: UUID) -> None:
        """Инвалидирует кэш для партии (best effort)."""
        if not self._cache_service or not self._cache_service.enabled:
            return
        try:
            await self._cache_service.delete(get_batch_key(batch_id, self._cache_service.key_prefix))
            await self._cache_service.delete_pattern(get_batches_list_pattern(self._cache_service.key_prefix))
        except Exception as e:
            logger.warning(f"Failed to invalidate cache for batch {batch_id}: {e}")
