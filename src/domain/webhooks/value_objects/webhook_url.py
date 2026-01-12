from dataclasses import dataclass

from src.domain.common.exceptions import EmptyFieldError
from src.domain.common.value_objects import ValueObject
from src.domain.webhooks.exceptions import WebhookSubscriptionInvalidUrlError


@dataclass(frozen=True, slots=True)
class WebhookUrl(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise EmptyFieldError("URL webhook не может быть пустым")

        if not self.value.startswith(("http://", "https://")):
            raise WebhookSubscriptionInvalidUrlError(self.value)

    def __str__(self) -> str:
        return self.value
