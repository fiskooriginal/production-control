from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.presentation.api.schemas.query_params import PaginationParams, SortParams
from src.presentation.api.schemas.work_centers import (
    CreateWorkCenterRequest,
    ListWorkCentersResponse,
    UpdateWorkCenterRequest,
    WorkCenterFiltersParams,
    WorkCenterResponse,
)
from src.presentation.di.work_centers import (
    create_work_center,
    delete_work_center,
    get_work_center,
    list_work_centers,
    update_work_center,
)
from src.presentation.mappers.query_params import build_list_work_centers_query
from src.presentation.mappers.work_centers import (
    create_request_to_input_dto,
    domain_to_response,
    update_request_to_input_dto,
)

router = APIRouter(prefix="/api/work_centers", tags=["work-centers"])


@router.post("", response_model=WorkCenterResponse, status_code=status.HTTP_201_CREATED)
async def create_work_center(request: CreateWorkCenterRequest, command: create_work_center) -> WorkCenterResponse:
    """
    Создает новый рабочий центр.
    """
    input_dto = create_request_to_input_dto(request)
    work_center_entity = await command.execute(input_dto)
    return domain_to_response(work_center_entity)


@router.get("/{work_center_id}", response_model=WorkCenterResponse)
async def get_work_center(work_center_id: UUID, query_handler: get_work_center) -> WorkCenterResponse:
    """
    Получает рабочий центр по ID.
    """
    work_center_dto = await query_handler.execute(work_center_id)
    return domain_to_response(work_center_dto)


@router.patch("/{work_center_id}", response_model=WorkCenterResponse)
async def update_work_center(
    work_center_id: UUID, request: UpdateWorkCenterRequest, command: update_work_center
) -> WorkCenterResponse:
    """
    Обновляет рабочий центр.
    """
    input_dto = update_request_to_input_dto(work_center_id, request)
    work_center_entity = await command.execute(input_dto)
    return domain_to_response(work_center_entity)


@router.delete("/{work_center_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_work_center(work_center_id: UUID, command: delete_work_center) -> None:
    """
    Удаляет рабочий центр.
    """

    await command.execute(work_center_id)


@router.get("", response_model=ListWorkCentersResponse)
async def list_work_centers(
    query_handler: list_work_centers,
    filter_params: WorkCenterFiltersParams = Depends(),
    pagination_params: PaginationParams = Depends(),
    sort_params: SortParams = Depends(),
) -> ListWorkCentersResponse:
    """
    Получает список рабочих центров с фильтрацией, пагинацией и сортировкой.
    """
    query = build_list_work_centers_query(filter_params, pagination_params, sort_params)
    result = await query_handler.execute(query)

    return ListWorkCentersResponse(
        items=[domain_to_response(dto) for dto in result.items],
        total=result.total,
        limit=result.limit,
        offset=result.offset,
    )
