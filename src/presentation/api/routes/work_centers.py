from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.application.work_centers.queries.use_cases import GetWorkCenterQueryUseCase, ListWorkCentersQueryUseCase
from src.application.work_centers.use_cases import (
    CreateWorkCenterUseCase,
    DeleteWorkCenterUseCase,
    UpdateWorkCenterUseCase,
)
from src.presentation.api.dependencies import (
    get_create_work_center_use_case,
    get_delete_work_center_use_case,
    get_list_work_centers_query_use_case,
    get_update_work_center_use_case,
    get_work_center_query_use_case,
)
from src.presentation.api.schemas.query_params import PaginationParams, SortParams
from src.presentation.api.schemas.work_centers import (
    CreateWorkCenterRequest,
    ListWorkCentersResponse,
    UpdateWorkCenterRequest,
    WorkCenterFiltersParams,
    WorkCenterResponse,
)
from src.presentation.mappers.query_params import build_list_work_centers_query
from src.presentation.mappers.query_responses import work_center_read_dto_to_response
from src.presentation.mappers.work_centers import (
    create_request_to_input_dto,
    entity_to_response,
    update_request_to_input_dto,
)

router = APIRouter(prefix="/api/work_centers", tags=["work-centers"])


@router.post("", response_model=WorkCenterResponse, status_code=status.HTTP_201_CREATED)
async def create_work_center(
    request: CreateWorkCenterRequest,
    use_case: CreateWorkCenterUseCase = Depends(get_create_work_center_use_case),
) -> WorkCenterResponse:
    """
    Создает новый рабочий центр.
    """
    input_dto = create_request_to_input_dto(request)
    work_center_entity = await use_case.execute(input_dto)
    return entity_to_response(work_center_entity)


@router.get("/{work_center_id}", response_model=WorkCenterResponse)
async def get_work_center(
    work_center_id: UUID,
    use_case: GetWorkCenterQueryUseCase = Depends(get_work_center_query_use_case),
) -> WorkCenterResponse:
    """
    Получает рабочий центр по ID.
    """
    work_center_dto = await use_case.execute(work_center_id)
    return work_center_read_dto_to_response(work_center_dto)


@router.patch("/{work_center_id}", response_model=WorkCenterResponse)
async def update_work_center(
    work_center_id: UUID,
    request: UpdateWorkCenterRequest,
    use_case: UpdateWorkCenterUseCase = Depends(get_update_work_center_use_case),
) -> WorkCenterResponse:
    """
    Обновляет рабочий центр.
    """
    input_dto = update_request_to_input_dto(work_center_id, request)
    work_center_entity = await use_case.execute(input_dto)
    return entity_to_response(work_center_entity)


@router.delete("/{work_center_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_work_center(
    work_center_id: UUID,
    use_case: DeleteWorkCenterUseCase = Depends(get_delete_work_center_use_case),
) -> None:
    """
    Удаляет рабочий центр.
    """

    await use_case.execute(work_center_id)


@router.get("", response_model=ListWorkCentersResponse)
async def list_work_centers(
    filter_params: WorkCenterFiltersParams = Depends(),
    pagination_params: PaginationParams = Depends(),
    sort_params: SortParams = Depends(),
    use_case: ListWorkCentersQueryUseCase = Depends(get_list_work_centers_query_use_case),
) -> ListWorkCentersResponse:
    """
    Получает список рабочих центров с фильтрацией, пагинацией и сортировкой.
    """
    query = build_list_work_centers_query(filter_params, pagination_params, sort_params)
    result = await use_case.execute(query)

    return ListWorkCentersResponse(
        items=[work_center_read_dto_to_response(dto) for dto in result.items],
        total=result.total,
        limit=result.limit,
        offset=result.offset,
    )
