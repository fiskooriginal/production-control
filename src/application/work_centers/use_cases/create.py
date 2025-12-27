from src.application.common.uow import UnitOfWorkProtocol
from src.application.work_centers.dtos import CreateWorkCenterInputDTO
from src.application.work_centers.mappers import input_dto_to_entity
from src.core.logging import get_logger
from src.domain.common.exceptions import InvalidStateError
from src.domain.work_centers.entities import WorkCenterEntity

logger = get_logger("use_case.work_centers")


class CreateWorkCenterUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, input_dto: CreateWorkCenterInputDTO) -> WorkCenterEntity:
        """Создает новый рабочий центр"""
        logger.info(f"Creating work center: identifier={input_dto.identifier}")
        try:
            async with self._uow:
                existing = await self._uow.work_centers.get_by_identifier(input_dto.identifier)
                if existing is not None:
                    raise InvalidStateError(f"Рабочий центр с идентификатором {input_dto.identifier} уже существует")

                work_center_entity = input_dto_to_entity(input_dto)

                result = await self._uow.work_centers.create(work_center_entity)
                logger.info(f"Work center created successfully: work_center_id={result.uuid}")
                return result
        except Exception as e:
            logger.exception(f"Failed to create work center: {e}")
            raise
