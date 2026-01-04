from uuid import UUID

from src.application.common.uow.interfaces import UnitOfWorkProtocol
from src.core.logging import get_logger

logger = get_logger("command.webhooks")


class DeleteWebhookSubscriptionCommand:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, subscription_id: UUID) -> None:
        """Удаляет подписку на webhook"""
        logger.info(f"Deleting webhook subscription: subscription_id={subscription_id}")
        try:
            async with self._uow:
                await self._uow.webhook_subscriptions.get_or_raise(subscription_id)

                await self._uow.webhook_subscriptions.delete(subscription_id)
                logger.info(f"Webhook subscription deleted successfully: subscription_id={subscription_id}")
        except Exception as e:
            logger.exception(f"Failed to delete webhook subscription: {e}")
            raise
