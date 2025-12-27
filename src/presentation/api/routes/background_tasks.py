from fastapi import APIRouter, status

from src.infrastructure.celery.app import celery_app
from src.presentation.api.schemas.background_tasks import TaskStatusResponse

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
    task_result = celery_app.AsyncResult(task_id)

    if task_result.state == "PENDING":
        return TaskStatusResponse(
            task_id=task_id,
            status="PENDING",
            result=None,
        )
    elif task_result.state == "PROGRESS":
        meta = task_result.info or {}
        return TaskStatusResponse(
            task_id=task_id,
            status="PROGRESS",
            result=meta,
        )
    elif task_result.state == "SUCCESS":
        return TaskStatusResponse(
            task_id=task_id,
            status="SUCCESS",
            result=task_result.result,
        )
    elif task_result.state == "FAILURE":
        return TaskStatusResponse(
            task_id=task_id,
            status="FAILURE",
            result={"error": str(task_result.info)} if task_result.info else None,
        )
    else:
        return TaskStatusResponse(
            task_id=task_id,
            status=task_result.state,
            result=task_result.info,
        )
