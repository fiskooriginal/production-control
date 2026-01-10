from celery.result import AsyncResult
from fastapi import APIRouter, status

from src.infrastructure.background_tasks import states
from src.infrastructure.background_tasks.app import celery_app
from src.presentation.v1.background_tasks.schemas import TaskStatusResponse

router = APIRouter(prefix="/background_tasks", tags=["background_tasks"])


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
