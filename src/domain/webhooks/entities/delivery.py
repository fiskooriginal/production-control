from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.core.time import datetime_now
from src.domain.common.entities import BaseEntity
from src.domain.common.enums import EventTypesEnum
from src.domain.common.exceptions import InvalidStateError
from src.domain.webhooks.enums import WebhookStatus
from src.domain.webhooks.value_objects import Attempts, HttpStatusCode, WebhookPayload


@dataclass(slots=True, kw_only=True)
class WebhookDeliveryEntity(BaseEntity):
    subscription_id: UUID
    event_type_id: UUID
    event_type: EventTypesEnum
    payload: WebhookPayload
    status: WebhookStatus
    attempts: Attempts = field(default_factory=lambda: Attempts(value=0))
    response_status: HttpStatusCode | None = None
    response_body: str | None = None
    error_message: str | None = None
    delivered_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.status == WebhookStatus.SUCCESS:
            if self.delivered_at is None:
                raise InvalidStateError("Время доставки должно быть установлено для успешной доставки")
            if self.response_status is None:
                raise InvalidStateError("HTTP статус должен быть установлен для успешной доставки")

    def mark_success(self, response_status: int, response_body: str, delivered_at: datetime | None = None) -> None:
        """Отмечает доставку как успешную"""
        if delivered_at is None:
            delivered_at = datetime_now()

        self.status = WebhookStatus.SUCCESS
        self.response_status = HttpStatusCode(value=response_status)
        self.response_body = response_body
        self.delivered_at = delivered_at
        self.error_message = None
        self.updated_at = datetime_now()

    def mark_failed(self, error_message: str) -> None:
        """Отмечает доставку как неудачную"""
        self.status = WebhookStatus.FAILED
        self.error_message = error_message
        self.updated_at = datetime_now()

    def increment_attempts(self) -> None:
        """Увеличивает количество попыток"""
        self.attempts = Attempts(value=self.attempts.value + 1)
        self.updated_at = datetime_now()
