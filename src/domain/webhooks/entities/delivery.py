from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.domain.shared.entities import BaseEntity
from src.domain.shared.exceptions import EmptyFieldError, InvalidStateError, InvalidValueError
from src.domain.webhooks.entities.subscription import WebhookSubscriptionEntity
from src.domain.webhooks.enums import WebhookEventType, WebhookStatus


@dataclass(frozen=True, slots=True, kw_only=True)
class WebhookDeliveryEntity(BaseEntity):
    subscription: WebhookSubscriptionEntity
    event_type: WebhookEventType
    payload: dict[str, Any]
    status: WebhookStatus
    attempts: int = 0
    response_status: int | None = None
    response_body: str | None = None
    error_message: str | None = None
    delivered_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.payload:
            raise EmptyFieldError("Полезная нагрузка не может быть пустой")

        if self.attempts < 0:
            raise InvalidValueError("Количество попыток должно быть >= 0")

        if self.response_status is not None and not (100 <= self.response_status <= 599):
            raise InvalidValueError("HTTP статус должен быть в диапазоне 100-599")

        if self.status == WebhookStatus.SUCCESS:
            if self.delivered_at is None:
                raise InvalidStateError("Время доставки должно быть установлено для успешной доставки")
            if self.response_status is None:
                raise InvalidStateError("HTTP статус должен быть установлен для успешной доставки")
