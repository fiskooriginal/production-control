from dataclasses import dataclass

from src.domain.common.enums import EventTypesEnum
from src.domain.common.value_objects import ValueObject
from src.domain.webhooks.exceptions import WebhookSubscriptionInvalidEventsError


@dataclass(frozen=True, slots=True)
class WebhookEvents(ValueObject):
    value: list[EventTypesEnum]

    def __post_init__(self) -> None:
        if not self.value:
            raise WebhookSubscriptionInvalidEventsError("Список событий не может быть пустым")

        if not all(isinstance(event, EventTypesEnum) for event in self.value):
            raise WebhookSubscriptionInvalidEventsError("Все события должны быть типа EventTypesEnum")

    def __str__(self) -> str:
        return str([event.value for event in self.value])
