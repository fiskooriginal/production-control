from uuid import UUID

from celery.result import AsyncResult
from fastapi import APIRouter, status

from src.infrastructure.background_tasks import states
from src.infrastructure.background_tasks.app import celery_app
from src.infrastructure.background_tasks.tasks import aggregate_batch as aggregate_batch_task
from src.presentation.api.schemas.background_tasks import TaskStartedResponse, TaskStatusResponse
from src.presentation.api.schemas.batches import AggregateBatchTaskRequest

router = APIRouter(prefix="/api/background_tasks", tags=["background_tasks"])


@router.get("/{task_id}", response_model=TaskStatusResponse, status_code=status.HTTP_200_OK)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    """
    Получает статус фоновой задачи по её ID.

    Статусы:
    - PENDING: задача в очереди
    - PROGRESS: задача выполняется (содержит прогресс)
    - SUCCESS: задача завершена успешно (содержит результат)
    - FAILURE: задача завершена с ошибкой
    """
    task_result = AsyncResult(task_id, app=celery_app)

    status = task_result.state
    if status == states.PENDING:
        return TaskStatusResponse(task_id=task_id, status=status)
    elif status == states.PROGRESS:
        info = task_result.info or {}
        return TaskStatusResponse(task_id=task_id, status=status, result=info)
    elif status == states.SUCCESS:
        result = task_result.result
        return TaskStatusResponse(task_id=task_id, status=status, result=result)
    elif status == states.FAILURE:
        result = {"error": str(task_result.info)} if task_result.info else None
        return TaskStatusResponse(task_id=task_id, status=status, result=result)
    return TaskStatusResponse(task_id=task_id, status=status, result=task_result.info)


@router.patch("/aggregate_batch/{batch_id}", response_model=TaskStartedResponse, status_code=status.HTTP_202_ACCEPTED)
async def aggregate_batch(
    batch_id: UUID,
    request: AggregateBatchTaskRequest,
) -> TaskStartedResponse:
    """
    Запускает фоновую задачу для агрегации партии и продуктов в ней.

    Если указаны unique_codes, агрегируются только указанные продукты.
    Если unique_codes не указан, агрегируются все продукты партии.
    """
    aggregated_at_str = None
    if request.aggregated_at:
        aggregated_at_str = request.aggregated_at.isoformat()

    task = aggregate_batch_task.delay(
        batch_id=str(batch_id), unique_codes=request.unique_codes, aggregated_at=aggregated_at_str
    )

    return TaskStartedResponse(
        task_id=task.id,
        status=states.PENDING,
        message="Aggregation task started",
    )
