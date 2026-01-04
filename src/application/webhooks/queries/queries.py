from dataclasses import dataclass
from uuid import UUID

from src.application.webhooks.queries.filters import WebhookReadFilters
from src.domain.common.queries import PaginationSpec


@dataclass(frozen=True, slots=True, kw_only=True)
class ListWebhookSubscriptionsQuery:
    filters: WebhookReadFilters | None = None
    pagination: PaginationSpec | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ListWebhookDeliveriesQuery:
    subscription_id: UUID
    pagination: PaginationSpec | None = None
