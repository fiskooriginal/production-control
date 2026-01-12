from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.webhooks.entities.delivery import WebhookDeliveryEntity
from src.domain.webhooks.interfaces.delivery import WebhookDeliveryRepositoryProtocol
from src.infrastructure.persistence.mappers.webhooks.delivery import to_domain_entity, to_persistence_model
from src.infrastructure.persistence.models.webhook import WebhookDelivery
from src.infrastructure.persistence.repositories.base import BaseRepository


class WebhookDeliveryRepository(
    BaseRepository[WebhookDeliveryEntity, WebhookDelivery], WebhookDeliveryRepositoryProtocol
):
    def __init__(self, session: AsyncSession):
        super().__init__(session, WebhookDelivery, to_domain_entity, to_persistence_model)
