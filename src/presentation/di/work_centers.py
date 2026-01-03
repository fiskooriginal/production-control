from typing import Annotated

from fastapi import Depends

from src.application.work_centers.commands.create import CreateWorkCenterCommand
from src.application.work_centers.commands.delete import DeleteWorkCenterCommand
from src.application.work_centers.commands.update import UpdateWorkCenterCommand
from src.application.work_centers.queries.handlers import GetWorkCenterQueryHandler, ListWorkCentersQueryHandler
from src.infrastructure.persistence.queries.work_centers import WorkCenterQueryService
from src.presentation.di.common import async_session, uow


# Commands
async def get_create_work_center_command(uow: uow) -> CreateWorkCenterCommand:
    """Dependency для CreateWorkCenterCommand"""
    return CreateWorkCenterCommand(uow)


async def get_update_work_center_command(uow: uow) -> UpdateWorkCenterCommand:
    """Dependency для UpdateWorkCenterCommand"""
    return UpdateWorkCenterCommand(uow)


async def get_delete_work_center_command(uow: uow) -> DeleteWorkCenterCommand:
    """Dependency для DeleteWorkCenterCommand"""
    return DeleteWorkCenterCommand(uow)


# Query Services
async def get_work_center_query_service(session: async_session) -> WorkCenterQueryService:
    """Dependency для WorkCenterQueryService"""
    return WorkCenterQueryService(session)


work_center_query = Annotated[WorkCenterQueryService, Depends(get_work_center_query_service)]


async def get_list_work_centers_query_handler(
    query_service: work_center_query,
) -> ListWorkCentersQueryHandler:
    """Dependency для ListWorkCentersQueryHandler"""
    return ListWorkCentersQueryHandler(query_service)


async def get_work_center_query_handler(query_service: work_center_query) -> GetWorkCenterQueryHandler:
    """Dependency для GetWorkCenterQueryHandler"""
    return GetWorkCenterQueryHandler(query_service)


# Query Handlers
list_work_centers = Annotated[ListWorkCentersQueryHandler, Depends(get_list_work_centers_query_handler)]
get_work_center = Annotated[GetWorkCenterQueryHandler, Depends(get_work_center_query_handler)]

# Commands
create_work_center = Annotated[CreateWorkCenterCommand, Depends(get_create_work_center_command)]
update_work_center = Annotated[UpdateWorkCenterCommand, Depends(get_update_work_center_command)]
delete_work_center = Annotated[DeleteWorkCenterCommand, Depends(get_delete_work_center_command)]
