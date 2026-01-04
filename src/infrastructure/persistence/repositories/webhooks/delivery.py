from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.common.exceptions import DoesNotExistError
from src.domain.webhooks.entities.delivery import WebhookDeliveryEntity
from src.domain.webhooks.interfaces.delivery import WebhookDeliveryRepositoryProtocol
from src.infrastructure.common.exceptions import DatabaseException
from src.infrastructure.persistence.mappers.webhooks.delivery import (
    to_domain_entity_delivery,
    to_persistence_model_delivery,
)
from src.infrastructure.persistence.models.webhook import WebhookDelivery


class WebhookDeliveryRepository(WebhookDeliveryRepositoryProtocol):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, domain_entity: WebhookDeliveryEntity) -> WebhookDeliveryEntity:
        """Создает новую доставку webhook в репозитории"""
        delivery_model = to_persistence_model_delivery(domain_entity)

        try:
            self._session.add(delivery_model)
            await self._session.flush()
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при создании доставки webhook: {e}") from e

        return to_domain_entity_delivery(delivery_model)

    async def update(self, domain_entity: WebhookDeliveryEntity) -> WebhookDeliveryEntity:
        """Обновляет существующую доставку webhook"""
        delivery_model = await self._session.get(WebhookDelivery, domain_entity.uuid)
        if delivery_model is None:
            raise DoesNotExistError(f"Доставка webhook с UUID {domain_entity.uuid} не найдена")

        updated_model = to_persistence_model_delivery(domain_entity)
        for key, value in updated_model.model_dump(exclude={"uuid", "created_at"}).items():
            setattr(delivery_model, key, value)

        try:
            await self._session.flush()
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при обновлении доставки webhook: {e}") from e

        return to_domain_entity_delivery(delivery_model)
