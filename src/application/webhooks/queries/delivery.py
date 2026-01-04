from typing import Protocol

from src.application.webhooks.queries.queries import ListWebhookDeliveriesQuery
from src.domain.common.queries import QueryResult
from src.domain.webhooks.entities.delivery import WebhookDeliveryEntity


class WebhookDeliveryQueryServiceProtocol(Protocol):
    """Протокол Query Service для WebhookDelivery (read-only операции)"""

    async def get_by_subscription_id(self, query: ListWebhookDeliveriesQuery) -> QueryResult[WebhookDeliveryEntity]:
        """Получает список доставок для подписки с пагинацией"""
        ...
