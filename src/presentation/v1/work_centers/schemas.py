from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, Field

from src.presentation.v1.common.schemas import TimestampSchema, UUIDSchema


class CreateWorkCenterRequest(BaseModel):
    """Request schema для создания рабочего центра"""

    identifier: str = Field(..., min_length=1, description="Идентификатор рабочего центра")
    name: str = Field(..., min_length=1, description="Название рабочего центра")


class UpdateWorkCenterRequest(BaseModel):
    """Request schema для обновления рабочего центра"""

    identifier: str | None = Field(None, min_length=1, description="Идентификатор рабочего центра")
    name: str | None = Field(None, min_length=1, description="Название рабочего центра")


class WorkCenterResponse(UUIDSchema, TimestampSchema, BaseModel):
    """Response schema для рабочего центра"""

    identifier: str = Field(..., description="Идентификатор рабочего центра")
    name: str = Field(..., description="Название рабочего центра")

    class Config:
        from_attributes = True


class WorkCenterFiltersParams(BaseModel):
    """Query параметры для фильтрации рабочих центров"""

    identifier: Annotated[str | None, Query(description="Фильтр по идентификатору")] = None


class ListWorkCentersResponse(BaseModel):
    """Response schema для списка рабочих центров"""

    items: list[WorkCenterResponse] = Field(..., description="Список рабочих центров")
    total: int = Field(..., description="Общее количество рабочих центров")
    limit: int | None = Field(None, description="Лимит элементов на странице")
    offset: int | None = Field(None, description="Смещение от начала")

    class Config:
        from_attributes = True
