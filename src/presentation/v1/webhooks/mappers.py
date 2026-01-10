from uuid import UUID

from src.application.webhooks.dtos.create_subscription import CreateWebhookSubscriptionInputDTO
from src.application.webhooks.queries.filters import WebhookReadFilters
from src.application.webhooks.queries.queries import ListWebhookDeliveriesQuery, ListWebhookSubscriptionsQuery
from src.domain.webhooks.entities.delivery import WebhookDeliveryEntity
from src.domain.webhooks.entities.subscription import WebhookSubscriptionEntity
from src.presentation.exceptions import SerializationException
from src.presentation.v1.common.mappers import pagination_params_to_spec
from src.presentation.v1.common.schemas import PaginationParams
from src.presentation.v1.webhooks.schemas import (
    CreateWebhookSubscriptionRequest,
    WebhookDeliveryResponse,
    WebhookFiltersParams,
    WebhookSubscriptionResponse,
)


def create_subscription_request_to_input_dto(
    request: CreateWebhookSubscriptionRequest,
) -> CreateWebhookSubscriptionInputDTO:
    """Конвертирует Pydantic CreateWebhookSubscriptionRequest в Application InputDTO"""
    try:
        return CreateWebhookSubscriptionInputDTO(
            url=request.url,
            events=request.events,
            secret_key=request.secret_key,
            is_active=request.is_active,
            retry_count=request.retry_count,
            timeout=request.timeout,
        )
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации CreateWebhookSubscriptionRequest: {e}") from e


def subscription_entity_to_response(entity: WebhookSubscriptionEntity) -> WebhookSubscriptionResponse:
    """Конвертирует Domain WebhookSubscriptionEntity в Pydantic Response"""
    try:
        return WebhookSubscriptionResponse(
            uuid=entity.uuid,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            url=entity.url.value,
            events=list(entity.events),
            is_active=entity.is_active,
            retry_count=entity.retry_count.value,
            timeout=entity.timeout.value,
        )
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации WebhookSubscriptionEntity в response: {e}") from e


def delivery_entity_to_response(entity: WebhookDeliveryEntity) -> WebhookDeliveryResponse:
    """Конвертирует Domain WebhookDeliveryEntity в Pydantic Response"""
    try:
        response_status = None
        if entity.response_status is not None:
            response_status = entity.response_status.value

        return WebhookDeliveryResponse(
            uuid=entity.uuid,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            subscription_id=entity.subscription_id,
            event_type=entity.event_type,
            payload=entity.payload.value,
            status=entity.status,
            attempts=entity.attempts.value,
            response_status=response_status,
            response_body=entity.response_body,
            error_message=entity.error_message,
            delivered_at=entity.delivered_at,
        )
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации WebhookDeliveryEntity в response: {e}") from e


def webhook_filters_params_to_query(params: WebhookFiltersParams) -> WebhookReadFilters | None:
    """Конвертирует WebhookFiltersParams в WebhookReadFilters"""
    try:
        if params.event_type is not None:
            return WebhookReadFilters(event_type=params.event_type)
        return None
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации WebhookFiltersParams: {e}") from e


def build_list_webhook_subscriptions_query(
    filter_params: WebhookFiltersParams,
    pagination_params: PaginationParams,
) -> ListWebhookSubscriptionsQuery:
    """Создает ListWebhookSubscriptionsQuery из параметров запроса"""
    filters = webhook_filters_params_to_query(filter_params)
    pagination = pagination_params_to_spec(pagination_params)

    return ListWebhookSubscriptionsQuery(filters=filters, pagination=pagination)


def build_list_webhook_deliveries_query(
    subscription_id: UUID,
    pagination_params: PaginationParams,
) -> ListWebhookDeliveriesQuery:
    """Создает ListWebhookDeliveriesQuery из параметров запроса"""
    pagination = pagination_params_to_spec(pagination_params)

    return ListWebhookDeliveriesQuery(subscription_id=subscription_id, pagination=pagination)
