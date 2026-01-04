from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field

from src.domain.common.enums import EventTypesEnum
from src.domain.webhooks.enums import WebhookStatus
from src.presentation.api.schemas.base import TimestampSchema, UUIDSchema


class WebhookTestResponse(BaseModel):
    """Ответ тестового эндпоинта для webhooks"""

    status: str
    received_at: str
    event: str | None
    signature_valid: bool | None
    headers: dict[str, str]
    payload: dict[str, Any]


class CreateWebhookSubscriptionRequest(BaseModel):
    """Request schema для создания подписки на webhook"""

    url: str = Field(..., min_length=1, description="URL для отправки webhook")
    events: list[EventTypesEnum] = Field(..., min_items=1, description="Список событий для подписки")
    secret_key: str = Field(..., min_length=1, description="Секретный ключ для подписи webhook")
    is_active: bool = Field(True, description="Активна ли подписка")
    retry_count: int = Field(3, ge=0, description="Количество повторов при неудачной доставке")
    timeout: int = Field(10, gt=0, description="Таймаут доставки в секундах")


class WebhookSubscriptionResponse(UUIDSchema, TimestampSchema, BaseModel):
    """Response schema для подписки на webhook"""

    url: str = Field(..., description="URL для отправки webhook")
    events: list[EventTypesEnum] = Field(..., description="Список событий для подписки")
    is_active: bool = Field(..., description="Активна ли подписка")
    retry_count: int = Field(..., description="Количество повторов при неудачной доставке")
    timeout: int = Field(..., description="Таймаут доставки в секундах")

    class Config:
        from_attributes = True


class WebhookFiltersParams(BaseModel):
    """Query параметры для фильтрации подписок на webhook"""

    event_type: Annotated[EventTypesEnum | None, Query(description="Фильтр по типу события")] = None


class ListWebhookSubscriptionsResponse(BaseModel):
    """Response schema для списка подписок на webhook"""

    items: list[WebhookSubscriptionResponse] = Field(..., description="Список подписок")
    total: int = Field(..., description="Общее количество подписок")
    limit: int | None = Field(None, description="Лимит элементов на странице")
    offset: int | None = Field(None, description="Смещение от начала")

    class Config:
        from_attributes = True


class WebhookDeliveryResponse(UUIDSchema, TimestampSchema, BaseModel):
    """Response schema для доставки webhook"""

    subscription_id: UUID = Field(..., description="ID подписки")
    event_type: EventTypesEnum = Field(..., description="Тип события")
    payload: dict[str, Any] = Field(..., description="Полезная нагрузка")
    status: WebhookStatus = Field(..., description="Статус доставки")
    attempts: int = Field(..., description="Количество попыток")
    response_status: int | None = Field(None, description="HTTP статус ответа")
    response_body: str | None = Field(None, description="Тело ответа")
    error_message: str | None = Field(None, description="Сообщение об ошибке")
    delivered_at: datetime | None = Field(None, description="Время доставки")

    class Config:
        from_attributes = True


class ListWebhookDeliveriesResponse(BaseModel):
    """Response schema для списка доставок webhook"""

    items: list[WebhookDeliveryResponse] = Field(..., description="Список доставок")
    total: int = Field(..., description="Общее количество доставок")
    limit: int | None = Field(None, description="Лимит элементов на странице")
    offset: int | None = Field(None, description="Смещение от начала")

    class Config:
        from_attributes = True
