from typing import Protocol

from src.domain.common.repository_protocol import BaseRepositoryProtocol
from src.domain.webhooks.entities.subscription import WebhookSubscriptionEntity


class WebhookSubscriptionRepositoryProtocol(BaseRepositoryProtocol[WebhookSubscriptionEntity], Protocol):
    """Протокол репозитория для WebhookSubscription (write-only операции)"""

    pass
