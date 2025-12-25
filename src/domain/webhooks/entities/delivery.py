from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from src.domain.shared.entities import BaseEntity
from src.domain.shared.exceptions import EmptyFieldError, InvalidStateError, InvalidValueError
from src.domain.shared.time import utc_now
from src.domain.webhooks.enums import WebhookEventType, WebhookStatus


@dataclass(slots=True, kw_only=True)
class WebhookDeliveryEntity(BaseEntity):
    subscription_id: UUID
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

    def mark_success(self, response_status: int, response_body: str, delivered_at: datetime | None = None) -> None:
        """Отмечает доставку как успешную"""
        if delivered_at is None:
            delivered_at = utc_now()
        if not (100 <= response_status <= 599):
            raise InvalidValueError("HTTP статус должен быть в диапазоне 100-599")
        self.status = WebhookStatus.SUCCESS
        self.response_status = response_status
        self.response_body = response_body
        self.delivered_at = delivered_at
        self.error_message = None
        self.updated_at = utc_now()

    def mark_failed(self, error_message: str) -> None:
        """Отмечает доставку как неудачную"""
        self.status = WebhookStatus.FAILED
        self.error_message = error_message
        self.updated_at = utc_now()

    def increment_attempts(self) -> None:
        """Увеличивает количество попыток"""
        self.attempts += 1
        self.updated_at = utc_now()
