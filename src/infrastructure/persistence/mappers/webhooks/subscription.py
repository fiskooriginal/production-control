from src.core.time import datetime_aware_to_naive, datetime_naive_to_aware
from src.domain.common.enums import EventTypesEnum
from src.domain.webhooks.entities.subscription import WebhookSubscriptionEntity
from src.domain.webhooks.value_objects import RetryCount, SecretKey, Timeout, WebhookUrl
from src.infrastructure.common.exceptions import MappingException
from src.infrastructure.persistence.models.webhook import WebhookSubscription


def to_domain_entity(subscription_model: WebhookSubscription) -> WebhookSubscriptionEntity:
    """Конвертирует persistence модель WebhookSubscription в domain entity WebhookSubscriptionEntity"""
    try:
        return WebhookSubscriptionEntity(
            uuid=subscription_model.uuid,
            created_at=datetime_naive_to_aware(subscription_model.created_at),
            updated_at=datetime_naive_to_aware(subscription_model.updated_at)
            if subscription_model.updated_at
            else None,
            url=WebhookUrl(subscription_model.url),
            events=list[EventTypesEnum](subscription_model.events),
            secret_key=SecretKey(subscription_model.secret_key),
            is_active=subscription_model.is_active,
            retry_count=RetryCount(subscription_model.retry_count),
            timeout=Timeout(subscription_model.timeout_seconds),
        )
    except Exception as e:
        raise MappingException(f"Ошибка маппинга persistence -> domain для WebhookSubscription: {e}") from e


def to_persistence_model(subscription_entity: WebhookSubscriptionEntity) -> WebhookSubscription:
    """Конвертирует domain entity WebhookSubscriptionEntity в persistence модель WebhookSubscription"""
    try:
        return WebhookSubscription(
            uuid=subscription_entity.uuid,
            created_at=datetime_aware_to_naive(subscription_entity.created_at),
            updated_at=datetime_aware_to_naive(subscription_entity.updated_at)
            if subscription_entity.updated_at
            else None,
            url=subscription_entity.url.value,
            events=[event.value for event in subscription_entity.events.value],
            secret_key=subscription_entity.secret_key.value,
            is_active=subscription_entity.is_active,
            retry_count=subscription_entity.retry_count.value,
            timeout_seconds=subscription_entity.timeout.value,
        )
    except Exception as e:
        raise MappingException(f"Ошибка маппинга domain -> persistence для WebhookSubscription: {e}") from e
