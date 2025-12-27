from typing import Any

from pydantic import BaseModel, Field


class TaskProgressResult(BaseModel):
    """Результат задачи в состоянии PROGRESS"""

    current: int = Field(..., description="Текущее количество обработанных элементов")
    total: int = Field(..., description="Общее количество элементов")
    progress: int = Field(..., description="Процент выполнения (0-100)")


class TaskFinalResult(BaseModel):
    """Финальный результат задачи в состоянии SUCCESS"""

    success: bool = Field(..., description="Успешность выполнения")
    total: int = Field(..., description="Общее количество элементов")
    aggregated: int = Field(..., description="Количество успешно агрегированных элементов")
    failed: int = Field(..., description="Количество неудачных элементов")
    errors: list[dict[str, str]] = Field(..., description="Список ошибок с кодами и причинами")


class TaskStatusResponse(BaseModel):
    """Ответ со статусом фоновой задачи"""

    task_id: str = Field(..., description="ID задачи")
    status: str = Field(..., description="Статус задачи: PENDING, PROGRESS, SUCCESS, FAILURE")
    result: TaskProgressResult | TaskFinalResult | dict[str, Any] | None = Field(
        None, description="Результат задачи (зависит от статуса)"
    )


class TaskStartedResponse(BaseModel):
    """Ответ при запуске фоновой задачи"""

    task_id: str = Field(..., description="ID задачи")
    status: str = Field(default="PENDING", description="Статус задачи")
    message: str = Field(default="Aggregation task started", description="Сообщение")
