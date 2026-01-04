from src.core.time import datetime_aware_to_naive, datetime_naive_to_aware
from src.domain.webhooks.entities.delivery import WebhookDeliveryEntity
from src.domain.webhooks.enums import WebhookEventType, WebhookStatus
from src.domain.webhooks.value_objects import Attempts, HttpStatusCode, WebhookPayload
from src.infrastructure.common.exceptions import MappingException
from src.infrastructure.persistence.models.webhook import WebhookDelivery


def to_domain_entity_delivery(delivery_model: WebhookDelivery) -> WebhookDeliveryEntity:
    """Конвертирует persistence модель WebhookDelivery в domain entity WebhookDeliveryEntity"""
    try:
        delivered_at = None
        if delivery_model.delivered_at:
            delivered_at = datetime_naive_to_aware(delivery_model.delivered_at)

        event_type = delivery_model.event_type
        if not isinstance(event_type, WebhookEventType):
            event_type = WebhookEventType(event_type)

        status = delivery_model.status
        if not isinstance(status, WebhookStatus):
            status = WebhookStatus(status)

        response_status = None
        if delivery_model.response_status is not None:
            response_status = HttpStatusCode(value=delivery_model.response_status)

        return WebhookDeliveryEntity(
            uuid=delivery_model.uuid,
            created_at=datetime_naive_to_aware(delivery_model.created_at),
            updated_at=datetime_naive_to_aware(delivery_model.updated_at) if delivery_model.updated_at else None,
            subscription_id=delivery_model.subscription_id,
            event_type=event_type,
            payload=WebhookPayload(value=delivery_model.payload),
            status=status,
            attempts=Attempts(value=delivery_model.attempts),
            response_status=response_status,
            response_body=delivery_model.response_body,
            error_message=delivery_model.error_message,
            delivered_at=delivered_at,
        )
    except Exception as e:
        raise MappingException(f"Ошибка маппинга persistence -> domain для WebhookDelivery: {e}") from e


def to_persistence_model_delivery(delivery_entity: WebhookDeliveryEntity) -> WebhookDelivery:
    """Конвертирует domain entity WebhookDeliveryEntity в persistence модель WebhookDelivery"""
    try:
        delivered_at = None
        if delivery_entity.delivered_at:
            delivered_at = datetime_aware_to_naive(delivery_entity.delivered_at)

        response_status = None
        if delivery_entity.response_status is not None:
            response_status = delivery_entity.response_status.value

        delivery_model = WebhookDelivery(
            uuid=delivery_entity.uuid,
            created_at=datetime_aware_to_naive(delivery_entity.created_at),
            updated_at=datetime_aware_to_naive(delivery_entity.updated_at) if delivery_entity.updated_at else None,
            subscription_id=delivery_entity.subscription_id,
            event_type=delivery_entity.event_type,
            payload=delivery_entity.payload.value,
            status=delivery_entity.status,
            attempts=delivery_entity.attempts.value,
            response_status=response_status,
            response_body=delivery_entity.response_body,
            error_message=delivery_entity.error_message,
            delivered_at=delivered_at,
        )

        return delivery_model
    except Exception as e:
        raise MappingException(f"Ошибка маппинга domain -> persistence для WebhookDelivery: {e}") from e
