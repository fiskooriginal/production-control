from typing import Protocol

from src.domain.webhooks.entities.delivery import WebhookDeliveryEntity


class WebhookDeliveryRepositoryProtocol(Protocol):
    """Протокол репозитория для WebhookDelivery (write-only операции)"""

    async def create(self, domain_entity: WebhookDeliveryEntity) -> WebhookDeliveryEntity:
        """Создает новую доставку webhook в репозитории"""
        ...

    async def update(self, domain_entity: WebhookDeliveryEntity) -> WebhookDeliveryEntity:
        """Обновляет существующую доставку webhook. Выбрасывает DoesNotExistError, если доставка не найдена."""
        ...
