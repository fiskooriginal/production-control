from dataclasses import dataclass

from src.domain.common.enums import EventTypesEnum


@dataclass(frozen=True, slots=True, kw_only=True)
class WebhookReadFilters:
    event_type: EventTypesEnum | None = None
