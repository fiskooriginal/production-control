from src.application.common.uow.interfaces import UnitOfWorkProtocol
from src.application.webhooks.dtos.create_subscription import CreateWebhookSubscriptionInputDTO
from src.application.webhooks.mappers import create_subscription_input_dto_to_entity
from src.core.logging import get_logger
from src.domain.webhooks.entities.subscription import WebhookSubscriptionEntity

logger = get_logger("command.webhooks")


class CreateWebhookSubscriptionCommand:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, input_dto: CreateWebhookSubscriptionInputDTO) -> WebhookSubscriptionEntity:
        """Создает новую подписку на webhook"""
        logger.info(f"Creating webhook subscription: url={input_dto.url}")
        subscription_id = None
        try:
            async with self._uow:
                subscription_entity = create_subscription_input_dto_to_entity(input_dto)

                result = await self._uow.webhook_subscriptions.create(subscription_entity)
                subscription_id = result.uuid
                logger.info(f"Webhook subscription created successfully: subscription_id={subscription_id}")

            return result
        except Exception as e:
            logger.exception(f"Failed to create webhook subscription: {e}")
            raise
