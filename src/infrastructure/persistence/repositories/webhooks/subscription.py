from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.webhooks.entities.subscription import WebhookSubscriptionEntity
from src.domain.webhooks.interfaces.subscription import WebhookSubscriptionRepositoryProtocol
from src.infrastructure.persistence.mappers.webhooks.subscription import to_domain_entity, to_persistence_model
from src.infrastructure.persistence.models.webhook import WebhookSubscription
from src.infrastructure.persistence.repositories.base import BaseRepository


class WebhookSubscriptionRepository(
    BaseRepository[WebhookSubscriptionEntity, WebhookSubscription], WebhookSubscriptionRepositoryProtocol
):
    def __init__(self, session: AsyncSession):
        super().__init__(session, WebhookSubscription, to_domain_entity, to_persistence_model)
