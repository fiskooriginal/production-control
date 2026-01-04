from dataclasses import dataclass

from src.domain.webhooks.enums import WebhookEventType


@dataclass(frozen=True, slots=True, kw_only=True)
class WebhookReadFilters:
    event_type: WebhookEventType | None = None
