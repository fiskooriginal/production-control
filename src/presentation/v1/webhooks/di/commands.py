from typing import Annotated

from fastapi import Depends

from src.application.webhooks.commands.create_subscription import CreateWebhookSubscriptionCommand
from src.application.webhooks.commands.delete_subscription import DeleteWebhookSubscriptionCommand
from src.presentation.v1.common.di import uow


async def get_create_webhook_subscription_command(unit_of_work: uow) -> CreateWebhookSubscriptionCommand:
    """Dependency для CreateWebhookSubscriptionCommand"""
    return CreateWebhookSubscriptionCommand(unit_of_work)


async def get_delete_webhook_subscription_command(unit_of_work: uow) -> DeleteWebhookSubscriptionCommand:
    """Dependency для DeleteWebhookSubscriptionCommand"""
    return DeleteWebhookSubscriptionCommand(unit_of_work)


create_webhook_subscription = Annotated[
    CreateWebhookSubscriptionCommand, Depends(get_create_webhook_subscription_command)
]
delete_webhook_subscription = Annotated[
    DeleteWebhookSubscriptionCommand, Depends(get_delete_webhook_subscription_command)
]
