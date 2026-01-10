from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel

from src.domain.common.queries import SortDirection


class UUIDSchema(BaseModel):
    uuid: UUID


class TimestampSchema(BaseModel):
    created_at: datetime
    updated_at: datetime | None = None


class PaginationParams(BaseModel):
    limit: Annotated[int | None, Query(ge=1, le=100, description="Лимит элементов на странице")] = 25
    offset: Annotated[int | None, Query(ge=0, description="Смещение от начала")] = 0


class SortParams(BaseModel):
    sort_field: Annotated[str | None, Query(description="Поле для сортировки")] = "created_at"
    sort_direction: Annotated[SortDirection | None, Query(description="Направление сортировки")] = SortDirection.DESC
