from src.application.uow import UnitOfWorkProtocol
from src.application.work_centers.dtos import UpdateWorkCenterInputDTO
from src.application.work_centers.mappers import update_dto_to_entity
from src.core.logging import get_logger
from src.domain.common.exceptions import InvalidStateError
from src.domain.work_centers.entities import WorkCenterEntity

logger = get_logger("use_case.work_centers")


class UpdateWorkCenterUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, input_dto: UpdateWorkCenterInputDTO) -> WorkCenterEntity:
        """Обновляет рабочий центр"""
        logger.info(f"Updating work center: work_center_id={input_dto.work_center_id}")
        try:
            async with self._uow:
                work_center = await self._uow.work_centers.get_or_raise(input_dto.work_center_id)

                if input_dto.identifier is not None and input_dto.identifier != work_center.identifier.value:
                    existing = await self._uow.work_centers.get_by_identifier(input_dto.identifier)
                    if existing is not None:
                        raise InvalidStateError(
                            f"Рабочий центр с идентификатором {input_dto.identifier} уже существует"
                        )

                updated_entity = update_dto_to_entity(work_center, input_dto)

                result = await self._uow.work_centers.update(updated_entity)
                logger.info(f"Work center updated successfully: work_center_id={input_dto.work_center_id}")
                return result
        except Exception as e:
            logger.exception(f"Failed to update work center: {e}")
            raise
