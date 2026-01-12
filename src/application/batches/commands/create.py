from src.application.batches.dtos.create import CreateBatchInputDTO
from src.application.batches.mappers import create_input_dto_to_entity
from src.application.common.uow.interfaces import UnitOfWorkProtocol
from src.core.logging import get_logger
from src.domain.batches import BatchEntity
from src.domain.batches.events import BatchCreatedEvent
from src.domain.batches.services import is_batch_exist, validate_shift_time_overlap
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

                if await is_batch_exist(batch_entity.batch_number, batch_entity.batch_date, self._uow.batches):
                    raise InvalidStateError(
                        f"Партия с номером {batch_entity.batch_number.value} и датой {batch_entity.batch_date} уже существует"
                    )

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
