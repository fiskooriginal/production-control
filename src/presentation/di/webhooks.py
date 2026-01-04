from typing import Annotated

from fastapi import Depends

from src.application.webhooks.commands.create_subscription import CreateWebhookSubscriptionCommand
from src.application.webhooks.commands.delete_subscription import DeleteWebhookSubscriptionCommand
from src.application.webhooks.queries.handlers import (
    GetWebhookSubscriptionQueryHandler,
    ListWebhookDeliveriesQueryHandler,
    ListWebhookSubscriptionsQueryHandler,
)
from src.infrastructure.persistence.queries.webhooks import WebhookDeliveryQueryService, WebhookSubscriptionQueryService
from src.presentation.di.common import async_session, uow


# Commands
async def get_create_webhook_subscription_command(uow: uow) -> CreateWebhookSubscriptionCommand:
    """Dependency для CreateWebhookSubscriptionCommand"""
    return CreateWebhookSubscriptionCommand(uow)


async def get_delete_webhook_subscription_command(uow: uow) -> DeleteWebhookSubscriptionCommand:
    """Dependency для DeleteWebhookSubscriptionCommand"""
    return DeleteWebhookSubscriptionCommand(uow)


# Query Services
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


# Query Handlers
list_webhook_subscriptions = Annotated[
    ListWebhookSubscriptionsQueryHandler, Depends(get_list_webhook_subscriptions_query_handler)
]
get_webhook_subscription = Annotated[
    GetWebhookSubscriptionQueryHandler, Depends(get_webhook_subscription_query_handler)
]
list_webhook_deliveries = Annotated[
    ListWebhookDeliveriesQueryHandler, Depends(get_list_webhook_deliveries_query_handler)
]

# Commands
create_webhook_subscription = Annotated[
    CreateWebhookSubscriptionCommand, Depends(get_create_webhook_subscription_command)
]
delete_webhook_subscription = Annotated[
    DeleteWebhookSubscriptionCommand, Depends(get_delete_webhook_subscription_command)
]
