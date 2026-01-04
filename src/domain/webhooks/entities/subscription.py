from dataclasses import dataclass, field

from src.core.time import datetime_now
from src.domain.common.entities import BaseEntity
from src.domain.common.enums import EventTypesEnum
from src.domain.webhooks.value_objects import RetryCount, SecretKey, Timeout, WebhookEvents, WebhookUrl


@dataclass(slots=True, kw_only=True)
class WebhookSubscriptionEntity(BaseEntity):
    url: WebhookUrl
    events: WebhookEvents
    secret_key: SecretKey
    is_active: bool = True
    retry_count: RetryCount = field(default_factory=lambda: RetryCount(value=3))
    timeout: Timeout = field(default_factory=lambda: Timeout(value=10))

    def activate(self) -> None:
        """Активирует подписку"""
        self.is_active = True
        self.updated_at = datetime_now()

    def deactivate(self) -> None:
        """Деактивирует подписку"""
        self.is_active = False
        self.updated_at = datetime_now()

    def update_events(self, events: list[EventTypesEnum]) -> None:
        """Обновляет список событий"""
        self.events = WebhookEvents(value=events)
        self.updated_at = datetime_now()
