from src.application.webhooks.queries.queries import ListWebhookSubscriptionsQuery
from src.application.webhooks.queries.subscription import WebhookSubscriptionQueryServiceProtocol
from src.core.logging import get_logger
from src.domain.common.queries import QueryResult
from src.domain.webhooks.entities.subscription import WebhookSubscriptionEntity

logger = get_logger("query.handler.webhooks")


class ListWebhookSubscriptionsQueryHandler:
    def __init__(self, query_service: WebhookSubscriptionQueryServiceProtocol):
        self._query_service = query_service

    async def execute(self, query: ListWebhookSubscriptionsQuery) -> QueryResult[WebhookSubscriptionEntity]:
        """Получает список всех подписок на webhook с пагинацией"""
        logger.debug(f"Listing webhook subscriptions: pagination={query.pagination}")
        try:
            result = await self._query_service.list(query)
            logger.debug(f"Listed {result.total} webhook subscriptions")
            return result
        except Exception as e:
            logger.exception(f"Failed to list webhook subscriptions: {e}")
            raise
