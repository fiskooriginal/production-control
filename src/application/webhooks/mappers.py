from src.application.webhooks.dtos.create_subscription import CreateWebhookSubscriptionInputDTO
from src.domain.webhooks.entities.subscription import WebhookSubscriptionEntity
from src.domain.webhooks.value_objects import RetryCount, SecretKey, Timeout, WebhookEvents, WebhookUrl


def create_subscription_input_dto_to_entity(dto: CreateWebhookSubscriptionInputDTO) -> WebhookSubscriptionEntity:
    """Маппер из CreateWebhookSubscriptionInputDTO в WebhookSubscriptionEntity"""
    return WebhookSubscriptionEntity(
        url=WebhookUrl(dto.url),
        events=WebhookEvents(dto.events),
        secret_key=SecretKey(dto.secret_key),
        is_active=dto.is_active,
        retry_count=RetryCount(dto.retry_count),
        timeout=Timeout(dto.timeout),
    )
