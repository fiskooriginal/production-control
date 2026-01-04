from dataclasses import dataclass

from src.domain.common.value_objects import ValueObject
from src.domain.webhooks.enums import WebhookEventType
from src.domain.webhooks.exceptions import WebhookSubscriptionInvalidEventsError


@dataclass(frozen=True, slots=True)
class WebhookEvents(ValueObject):
    value: list[WebhookEventType]

    def __post_init__(self) -> None:
        if not self.value:
            raise WebhookSubscriptionInvalidEventsError("Список событий не может быть пустым")

        if not all(isinstance(event, WebhookEventType) for event in self.value):
            raise WebhookSubscriptionInvalidEventsError("Все события должны быть типа WebhookEventType")

    def __str__(self) -> str:
        return str([event.value for event in self.value])
