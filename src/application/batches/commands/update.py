from uuid import UUID

from src.application.batches.dtos.update import UpdateBatchInputDTO
from src.application.common.uow import UnitOfWorkProtocol
from src.core.logging import get_logger
from src.core.time import datetime_now
from src.domain.batches.entities import BatchEntity
from src.domain.batches.services import validate_batch_number_uniqueness, validate_shift_time_overlap
from src.domain.batches.value_objects import (
    BatchNumber,
    EknCode,
    Nomenclature,
    Shift,
    TaskDescription,
    Team,
)
from src.domain.common.exceptions import InvalidStateError
from src.infrastructure.cache.keys.batches import get_batch_key, get_batches_list_pattern
from src.infrastructure.cache.protocol import CacheServiceProtocol

logger = get_logger("command.batches")


class UpdateBatchCommand:
    def __init__(self, uow: UnitOfWorkProtocol, cache_service: CacheServiceProtocol | None = None):
        self._uow = uow
        self._cache_service = cache_service

    async def execute(self, input_dto: UpdateBatchInputDTO) -> BatchEntity:
        """Обновляет партию частично: только указанные поля."""
        logger.info(f"Updating batch: batch_id={input_dto.batch_id}")
        try:
            async with self._uow:
                batch = await self._uow.batches.get_or_raise(input_dto.batch_id)

                if input_dto.task_description is not None:
                    batch.task_description = TaskDescription(input_dto.task_description)

                if input_dto.shift is not None:
                    batch.shift = Shift(input_dto.shift)

                if input_dto.team is not None:
                    batch.team = Team(input_dto.team)

                if input_dto.batch_number is not None:
                    new_batch_number = BatchNumber(input_dto.batch_number)
                    is_unique = await validate_batch_number_uniqueness(new_batch_number, self._uow.batches)
                    if not is_unique:
                        raise InvalidStateError(f"Партия с номером {new_batch_number.value} уже существует")
                    batch.batch_number = new_batch_number

                if input_dto.batch_date is not None:
                    batch.batch_date = input_dto.batch_date

                if input_dto.nomenclature is not None:
                    batch.nomenclature = Nomenclature(input_dto.nomenclature)

                if input_dto.ekn_code is not None:
                    batch.ekn_code = EknCode(input_dto.ekn_code)

                shift_time_changed = False
                if input_dto.shift_start is not None or input_dto.shift_end is not None:
                    start = input_dto.shift_start or batch.shift_time_range.start
                    end = input_dto.shift_end or batch.shift_time_range.end
                    batch.update_shift_time_range(start, end)
                    shift_time_changed = True

                if input_dto.work_center_id is not None:
                    await self._uow.work_centers.get_or_raise(input_dto.work_center_id)
                    batch.work_center_id = input_dto.work_center_id

                if input_dto.is_closed is not None:
                    if input_dto.is_closed:
                        batch.close()
                    else:
                        batch.open()

                if shift_time_changed:
                    is_valid = await validate_shift_time_overlap(batch, self._uow.batches)
                    if not is_valid:
                        raise InvalidStateError("Время смены пересекается с другой партией")

                batch.updated_at = datetime_now()

                result = await self._uow.batches.update(batch)
                logger.info(f"Batch updated successfully: batch_id={input_dto.batch_id}")

            await self._invalidate_batch_cache(input_dto.batch_id)
            return result
        except Exception as e:
            logger.exception(f"Failed to update batch: {e}")
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
