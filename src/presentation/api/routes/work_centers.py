from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.application.use_cases.work_centers import (
    CreateWorkCenterUseCase,
    DeleteWorkCenterUseCase,
    GetWorkCenterUseCase,
    ListWorkCentersUseCase,
    UpdateWorkCenterUseCase,
)
from src.presentation.api.dependencies import (
    get_create_work_center_use_case,
    get_delete_work_center_use_case,
    get_get_work_center_use_case,
    get_list_work_centers_use_case,
    get_update_work_center_use_case,
)
from src.presentation.api.schemas.query_params import PaginationParams, SortParams
from src.presentation.api.schemas.work_centers import (
    CreateWorkCenterRequest,
    ListWorkCentersResponse,
    UpdateWorkCenterRequest,
    WorkCenterFiltersParams,
    WorkCenterResponse,
)
from src.presentation.mappers.query_params import (
    pagination_params_to_spec,
    sort_params_to_spec,
    work_center_filters_params_to_dto,
)
from src.presentation.mappers.work_centers import (
    create_request_to_input_dto,
    entity_to_response,
    update_request_to_input_dto,
)

router = APIRouter(prefix="/work-centers", tags=["work-centers"])


@router.post("", response_model=WorkCenterResponse, status_code=status.HTTP_201_CREATED)
async def create_work_center(
    request: CreateWorkCenterRequest,
    use_case: CreateWorkCenterUseCase = Depends(get_create_work_center_use_case),
) -> WorkCenterResponse:
    """
    Создает новый рабочий центр.

    RESTful endpoint: POST /work-centers
    """
    input_dto = create_request_to_input_dto(request)
    work_center_entity = await use_case.execute(input_dto)
    return entity_to_response(work_center_entity)


@router.get("/{work_center_id}", response_model=WorkCenterResponse)
async def get_work_center(
    work_center_id: str,
    use_case: GetWorkCenterUseCase = Depends(get_get_work_center_use_case),
) -> WorkCenterResponse:
    """
    Получает рабочий центр по ID.

    RESTful endpoint: GET /work-centers/{work_center_id}
    """

    work_center_entity = await use_case.execute(UUID(work_center_id))
    return entity_to_response(work_center_entity)


@router.patch("/{work_center_id}", response_model=WorkCenterResponse)
async def update_work_center(
    work_center_id: str,
    request: UpdateWorkCenterRequest,
    use_case: UpdateWorkCenterUseCase = Depends(get_update_work_center_use_case),
) -> WorkCenterResponse:
    """
    Обновляет рабочий центр.

    RESTful endpoint: PATCH /work-centers/{work_center_id}
    """
    input_dto = update_request_to_input_dto(work_center_id, request)
    work_center_entity = await use_case.execute(input_dto)
    return entity_to_response(work_center_entity)


@router.delete("/{work_center_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_work_center(
    work_center_id: str,
    use_case: DeleteWorkCenterUseCase = Depends(get_delete_work_center_use_case),
) -> None:
    """
    Удаляет рабочий центр.

    RESTful endpoint: DELETE /work-centers/{work_center_id}
    """

    await use_case.execute(UUID(work_center_id))


@router.get("", response_model=ListWorkCentersResponse)
async def list_work_centers(
    filter_params: WorkCenterFiltersParams = Depends(),
    pagination_params: PaginationParams = Depends(),
    sort_params: SortParams = Depends(),
    use_case: ListWorkCentersUseCase = Depends(get_list_work_centers_use_case),
) -> ListWorkCentersResponse:
    """
    Получает список рабочих центров с фильтрацией, пагинацией и сортировкой.

    RESTful endpoint: GET /work-centers
    """
    filters = work_center_filters_params_to_dto(filter_params)
    pagination = pagination_params_to_spec(pagination_params)
    sort = sort_params_to_spec(sort_params)

    result = await use_case.execute(filters=filters, pagination=pagination, sort=sort)

    return ListWorkCentersResponse(
        items=[entity_to_response(entity) for entity in result.items],
        total=result.total,
        limit=result.limit,
        offset=result.offset,
    )
