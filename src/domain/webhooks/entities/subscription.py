from dataclasses import dataclass
from datetime import datetime

from src.domain.shared.entities import BaseEntity
from src.domain.shared.exceptions import EmptyFieldError, InvalidValueError
from src.domain.webhooks.enums import WebhookEventType
from src.domain.webhooks.exceptions import WebhookSubscriptionInvalidEventsError, WebhookSubscriptionInvalidUrlError


@dataclass(slots=True, kw_only=True)
class WebhookSubscriptionEntity(BaseEntity):
    url: str
    events: list[WebhookEventType]
    secret_key: str
    is_active: bool = True
    retry_count: int = 3
    timeout: int = 10

    def __post_init__(self) -> None:
        if not self.url or not self.url.strip():
            raise EmptyFieldError("URL webhook не может быть пустым")
        if not self.url.startswith(("http://", "https://")):
            raise WebhookSubscriptionInvalidUrlError(self.url)

        if not self.secret_key or not self.secret_key.strip():
            raise EmptyFieldError("Секретный ключ не может быть пустым")

        if not self.events:
            raise WebhookSubscriptionInvalidEventsError("список событий не может быть пустым")

        if not all(isinstance(event, WebhookEventType) for event in self.events):
            raise WebhookSubscriptionInvalidEventsError("все события должны быть типа WebhookEventType")

        if self.retry_count < 0:
            raise InvalidValueError("Количество повторов должно быть >= 0")

        if self.timeout <= 0:
            raise InvalidValueError("Таймаут должен быть > 0")

    def activate(self) -> None:
        """Активирует подписку"""
        self.is_active = True
        self.updated_at = datetime.now()

    def deactivate(self) -> None:
        """Деактивирует подписку"""
        self.is_active = False
        self.updated_at = datetime.now()

    def update_events(self, events: list[WebhookEventType]) -> None:
        """Обновляет список событий"""
        if not events:
            raise WebhookSubscriptionInvalidEventsError("список событий не может быть пустым")
        if not all(isinstance(event, WebhookEventType) for event in events):
            raise WebhookSubscriptionInvalidEventsError("все события должны быть типа WebhookEventType")
        self.events = events
        self.updated_at = datetime.now()
