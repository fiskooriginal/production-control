from typing import Annotated

from fastapi import Depends

from src.application.webhooks.queries.handlers import (
    GetWebhookSubscriptionQueryHandler,
    ListWebhookDeliveriesQueryHandler,
    ListWebhookSubscriptionsQueryHandler,
)
from src.infrastructure.persistence.queries.webhooks import WebhookDeliveryQueryService, WebhookSubscriptionQueryService
from src.presentation.v1.common.di import async_session


async def get_webhook_subscription_query_service(session: async_session) -> WebhookSubscriptionQueryService:
    """Dependency для WebhookSubscriptionQueryService"""
    return WebhookSubscriptionQueryService(session)


async def get_webhook_delivery_query_service(session: async_session) -> WebhookDeliveryQueryService:
    """Dependency для WebhookDeliveryQueryService"""
    return WebhookDeliveryQueryService(session)


webhook_subscription_query = Annotated[WebhookSubscriptionQueryService, Depends(get_webhook_subscription_query_service)]
webhook_delivery_query = Annotated[WebhookDeliveryQueryService, Depends(get_webhook_delivery_query_service)]


async def get_list_webhook_subscriptions_query_handler(
    query_service: webhook_subscription_query,
) -> ListWebhookSubscriptionsQueryHandler:
    """Dependency для ListWebhookSubscriptionsQueryHandler"""
    return ListWebhookSubscriptionsQueryHandler(query_service)


async def get_webhook_subscription_query_handler(
    query_service: webhook_subscription_query,
) -> GetWebhookSubscriptionQueryHandler:
    """Dependency для GetWebhookSubscriptionQueryHandler"""
    return GetWebhookSubscriptionQueryHandler(query_service)


async def get_list_webhook_deliveries_query_handler(
    query_service: webhook_delivery_query,
) -> ListWebhookDeliveriesQueryHandler:
    """Dependency для ListWebhookDeliveriesQueryHandler"""
    return ListWebhookDeliveriesQueryHandler(query_service)


list_webhook_subscriptions = Annotated[
    ListWebhookSubscriptionsQueryHandler, Depends(get_list_webhook_subscriptions_query_handler)
]
get_webhook_subscription = Annotated[
    GetWebhookSubscriptionQueryHandler, Depends(get_webhook_subscription_query_handler)
]
list_webhook_deliveries = Annotated[
    ListWebhookDeliveriesQueryHandler, Depends(get_list_webhook_deliveries_query_handler)
]
