from typing import Annotated

from fastapi import Depends

from src.application.work_centers.queries.handlers import GetWorkCenterQueryHandler, ListWorkCentersQueryHandler
from src.infrastructure.persistence.queries.work_centers import WorkCenterQueryService
from src.presentation.v1.common.di import async_session


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


list_work_centers = Annotated[ListWorkCentersQueryHandler, Depends(get_list_work_centers_query_handler)]
get_work_center = Annotated[GetWorkCenterQueryHandler, Depends(get_work_center_query_handler)]
