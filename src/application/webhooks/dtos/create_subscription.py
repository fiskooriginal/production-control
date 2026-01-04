from dataclasses import dataclass

from src.domain.common.enums import EventTypesEnum


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateWebhookSubscriptionInputDTO:
    url: str
    events: list[EventTypesEnum]
    secret_key: str
    is_active: bool = True
    retry_count: int = 3
    timeout: int = 10
