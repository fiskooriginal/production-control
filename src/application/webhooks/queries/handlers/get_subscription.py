from uuid import UUID

from src.application.webhooks.queries.subscription import WebhookSubscriptionQueryServiceProtocol
from src.core.logging import get_logger
from src.domain.common.exceptions import DoesNotExistError
from src.domain.webhooks.entities.subscription import WebhookSubscriptionEntity

logger = get_logger("query.handler.webhooks")


class GetWebhookSubscriptionQueryHandler:
    def __init__(self, query_service: WebhookSubscriptionQueryServiceProtocol):
        self._query_service = query_service

    async def execute(self, subscription_id: UUID) -> WebhookSubscriptionEntity:
        """Получает подписку на webhook по UUID"""
        logger.debug(f"Getting webhook subscription: subscription_id={subscription_id}")
        try:
            result = await self._query_service.get(subscription_id)
            if result is None:
                raise DoesNotExistError(f"Подписка на webhook с UUID {subscription_id} не найдена")
            logger.debug(f"Webhook subscription retrieved: subscription_id={subscription_id}")
            return result
        except DoesNotExistError:
            raise
        except Exception as e:
            logger.exception(f"Failed to get webhook subscription: {e}")
            raise
