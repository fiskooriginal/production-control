from src.application.batches.dtos import CreateBatchInputDTO
from src.application.batches.mappers import create_input_dto_to_entity
from src.application.common.uow import UnitOfWorkProtocol
from src.core.logging import get_logger
from src.domain.batches.entities import BatchEntity
from src.domain.batches.events import BatchCreatedEvent
from src.domain.batches.services import validate_batch_number_uniqueness, validate_shift_time_overlap
from src.domain.common.exceptions import InvalidStateError

logger = get_logger("command.batches")


class CreateBatchCommand:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, input_dto: CreateBatchInputDTO) -> BatchEntity:
        """Создает новую партию с автоматическим сохранением доменных событий в outbox"""
        logger.info(f"Creating batch: batch_number={input_dto.batch_number}")
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
                logger.info(f"Batch created successfully: batch_id={result.uuid}")
                return result
        except Exception as e:
            logger.exception(f"Failed to create batch: {e}")
            raise
