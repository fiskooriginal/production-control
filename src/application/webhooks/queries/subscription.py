from typing import Protocol
from uuid import UUID

from src.application.webhooks.queries.queries import ListWebhookSubscriptionsQuery
from src.domain.common.queries import QueryResult
from src.domain.webhooks.entities.subscription import WebhookSubscriptionEntity


class WebhookSubscriptionQueryServiceProtocol(Protocol):
    """Протокол Query Service для WebhookSubscription (read-only операции)"""

    async def get(self, subscription_id: UUID) -> WebhookSubscriptionEntity | None:
        """Получает подписку на webhook по UUID"""
        ...

    async def list(self, query: ListWebhookSubscriptionsQuery) -> QueryResult[WebhookSubscriptionEntity]:
        """Получает список всех подписок на webhook с пагинацией"""
        ...
