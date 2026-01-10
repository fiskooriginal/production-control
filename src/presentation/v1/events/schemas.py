from pydantic import BaseModel, Field

from src.presentation.v1.common.schemas import TimestampSchema, UUIDSchema


class EventTypeResponse(UUIDSchema, TimestampSchema, BaseModel):
    """Response schema для типа события"""

    name: str = Field(..., description="Название типа события")
    version: int = Field(..., description="Версия типа события")
    webhook_enabled: bool = Field(..., description="Включена ли отправка webhook для этого типа события")
    description: str | None = Field(None, description="Описание типа события")

    class Config:
        from_attributes = True


class ListEventsResponse(BaseModel):
    """Response schema для списка типов событий"""

    items: list[EventTypeResponse] = Field(..., description="Список типов событий")

    class Config:
        from_attributes = True
