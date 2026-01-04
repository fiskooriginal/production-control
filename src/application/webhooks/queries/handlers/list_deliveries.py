from src.application.webhooks.queries.delivery import WebhookDeliveryQueryServiceProtocol
from src.application.webhooks.queries.queries import ListWebhookDeliveriesQuery
from src.core.logging import get_logger
from src.domain.common.queries import QueryResult
from src.domain.webhooks.entities.delivery import WebhookDeliveryEntity

logger = get_logger("query.handler.webhooks")


class ListWebhookDeliveriesQueryHandler:
    def __init__(self, query_service: WebhookDeliveryQueryServiceProtocol):
        self._query_service = query_service

    async def execute(self, query: ListWebhookDeliveriesQuery) -> QueryResult[WebhookDeliveryEntity]:
        """Получает список доставок для подписки на webhook с пагинацией"""
        logger.debug(
            f"Listing webhook deliveries: subscription_id={query.subscription_id}, pagination={query.pagination}"
        )
        try:
            result = await self._query_service.get_by_subscription_id(query)
            logger.debug(f"Listed {result.total} webhook deliveries for subscription {query.subscription_id}")
            return result
        except Exception as e:
            logger.exception(f"Failed to list webhook deliveries: {e}")
            raise
