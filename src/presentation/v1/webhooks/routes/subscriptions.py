from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.presentation.v1.common.schemas import PaginationParams
from src.presentation.v1.webhooks.di.commands import create_webhook_subscription, delete_webhook_subscription
from src.presentation.v1.webhooks.di.queries import get_webhook_subscription, list_webhook_subscriptions
from src.presentation.v1.webhooks.mappers import (
    build_list_webhook_subscriptions_query,
    create_subscription_request_to_input_dto,
    subscription_entity_to_response,
)
from src.presentation.v1.webhooks.schemas import (
    CreateWebhookSubscriptionRequest,
    ListWebhookSubscriptionsResponse,
    WebhookFiltersParams,
    WebhookSubscriptionResponse,
)

router = APIRouter()


@router.post("", response_model=WebhookSubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook_subscription(
    request: CreateWebhookSubscriptionRequest, command: create_webhook_subscription
) -> WebhookSubscriptionResponse:
    """
    Создает новую подписку на webhook.
    """
    input_dto = create_subscription_request_to_input_dto(request)
    subscription_entity = await command.execute(input_dto)
    return subscription_entity_to_response(subscription_entity)


@router.get("", response_model=ListWebhookSubscriptionsResponse)
async def list_webhook_subscriptions(
    query_handler: list_webhook_subscriptions,
    filter_params: WebhookFiltersParams = Depends(),
    pagination_params: PaginationParams = Depends(),
) -> ListWebhookSubscriptionsResponse:
    """
    Получает список всех подписок на webhook с пагинацией и фильтрацией.
    """
    query = build_list_webhook_subscriptions_query(filter_params, pagination_params)
    result = await query_handler.execute(query)
    return ListWebhookSubscriptionsResponse(
        items=[subscription_entity_to_response(subscription) for subscription in result.items],
        total=result.total,
        limit=result.limit,
        offset=result.offset,
    )


@router.get("/{subscription_id}", response_model=WebhookSubscriptionResponse)
async def get_webhook_subscription(
    subscription_id: UUID, query_handler: get_webhook_subscription
) -> WebhookSubscriptionResponse:
    """
    Получает подписку на webhook по UUID.
    """
    subscription_entity = await query_handler.execute(subscription_id)
    return subscription_entity_to_response(subscription_entity)


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook_subscription(subscription_id: UUID, command: delete_webhook_subscription) -> None:
    """
    Удаляет подписку на webhook.
    """
    await command.execute(subscription_id)
