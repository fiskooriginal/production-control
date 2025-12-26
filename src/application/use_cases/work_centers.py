from uuid import UUID

from src.application.dtos.work_centers import CreateWorkCenterInputDTO, UpdateWorkCenterInputDTO
from src.application.mappers.work_centers import input_dto_to_entity, update_dto_to_entity
from src.application.uow import UnitOfWorkProtocol
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
                # Валидация уникальности identifier
                existing = await self._uow.work_centers.get_by_identifier(input_dto.identifier)
                if existing is not None:
                    raise InvalidStateError(f"Рабочий центр с идентификатором {input_dto.identifier} уже существует")

                # Создание domain_entity через маппер
                work_center_entity = input_dto_to_entity(input_dto)

                # Сохранение через репозиторий
                result = await self._uow.work_centers.create(work_center_entity)
                logger.info(f"Work center created successfully: work_center_id={result.uuid}")
                return result
        except Exception as e:
            logger.exception(f"Failed to create work center: {e}")
            raise


class UpdateWorkCenterUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, input_dto: UpdateWorkCenterInputDTO) -> WorkCenterEntity:
        """Обновляет рабочий центр"""
        logger.info(f"Updating work center: work_center_id={input_dto.work_center_id}")
        try:
            async with self._uow:
                # Загружаем domain_entity
                work_center = await self._uow.work_centers.get_or_raise(input_dto.work_center_id)

                # Если обновляется identifier, проверяем уникальность
                if input_dto.identifier is not None and input_dto.identifier != work_center.identifier.value:
                    existing = await self._uow.work_centers.get_by_identifier(input_dto.identifier)
                    if existing is not None:
                        raise InvalidStateError(
                            f"Рабочий центр с идентификатором {input_dto.identifier} уже существует"
                        )

                # Обновляем поля
                updated_entity = update_dto_to_entity(work_center, input_dto)

                # Сохраняем
                result = await self._uow.work_centers.update(updated_entity)
                logger.info(f"Work center updated successfully: work_center_id={input_dto.work_center_id}")
                return result
        except Exception as e:
            logger.exception(f"Failed to update work center: {e}")
            raise


class DeleteWorkCenterUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, work_center_id: UUID) -> None:
        """Удаляет рабочий центр"""
        logger.info(f"Deleting work center: work_center_id={work_center_id}")
        try:
            async with self._uow:
                # Проверяем существование
                await self._uow.work_centers.get_or_raise(work_center_id)
                # Удаляем
                await self._uow.work_centers.delete(work_center_id)
                logger.info(f"Work center deleted successfully: work_center_id={work_center_id}")
        except Exception as e:
            logger.exception(f"Failed to delete work center: {e}")
            raise
