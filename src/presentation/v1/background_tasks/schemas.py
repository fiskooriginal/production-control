from typing import Any

from pydantic import BaseModel, Field


class TaskStatusResponse(BaseModel):
    """Ответ со статусом фоновой задачи"""

    task_id: str = Field(..., description="ID задачи")
    status: str = Field(..., description="Статус задачи: PENDING, PROGRESS, SUCCESS, FAILURE")
    result: dict[str, Any] | None = Field(None, description="Результат задачи")


class TaskStartedResponse(BaseModel):
    """Ответ при запуске фоновой задачи"""

    task_id: str = Field(..., description="ID задачи")
    status: str = Field(default="PENDING", description="Статус задачи")
    message: str = Field(default="Task started", description="Сообщение")
