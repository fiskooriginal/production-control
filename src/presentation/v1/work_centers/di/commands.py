from typing import Annotated

from fastapi import Depends

from src.application.work_centers.commands.create import CreateWorkCenterCommand
from src.application.work_centers.commands.delete import DeleteWorkCenterCommand
from src.application.work_centers.commands.update import UpdateWorkCenterCommand
from src.infrastructure.persistence.queries.work_centers import WorkCenterQueryService
from src.presentation.v1.common.di import async_session, uow


async def get_create_work_center_command(unit_of_work: uow) -> CreateWorkCenterCommand:
    """Dependency для CreateWorkCenterCommand"""
    return CreateWorkCenterCommand(unit_of_work)


async def get_update_work_center_command(unit_of_work: uow) -> UpdateWorkCenterCommand:
    """Dependency для UpdateWorkCenterCommand"""
    return UpdateWorkCenterCommand(unit_of_work)


async def get_delete_work_center_command(unit_of_work: uow) -> DeleteWorkCenterCommand:
    """Dependency для DeleteWorkCenterCommand"""
    return DeleteWorkCenterCommand(unit_of_work)


async def get_work_center_query_service(session: async_session) -> WorkCenterQueryService:
    """Dependency для WorkCenterQueryService"""
    return WorkCenterQueryService(session)


create_work_center = Annotated[CreateWorkCenterCommand, Depends(get_create_work_center_command)]
update_work_center = Annotated[UpdateWorkCenterCommand, Depends(get_update_work_center_command)]
delete_work_center = Annotated[DeleteWorkCenterCommand, Depends(get_delete_work_center_command)]
