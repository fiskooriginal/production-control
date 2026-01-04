from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.common.exceptions import AlreadyExistsError, DoesNotExistError
from src.domain.webhooks.entities.subscription import WebhookSubscriptionEntity
from src.domain.webhooks.interfaces.subscription import WebhookSubscriptionRepositoryProtocol
from src.infrastructure.common.exceptions import DatabaseException
from src.infrastructure.persistence.mappers.webhooks.subscription import (
    to_domain_entity_subscription,
    to_persistence_model_subscription,
)
from src.infrastructure.persistence.models.webhook import WebhookSubscription


class WebhookSubscriptionRepository(WebhookSubscriptionRepositoryProtocol):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_or_raise(self, uuid: UUID) -> WebhookSubscriptionEntity:
        """Получает подписку по UUID для write-операций"""
        try:
            subscription_model = await self._session.get(WebhookSubscription, uuid)
            if subscription_model is None:
                raise DoesNotExistError(f"Подписка на webhook с UUID {uuid} не найдена")
            return to_domain_entity_subscription(subscription_model)
        except DoesNotExistError:
            raise
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении подписки на webhook: {e}") from e

    async def create(self, domain_entity: WebhookSubscriptionEntity) -> WebhookSubscriptionEntity:
        """Создает новую подписку на webhook в репозитории"""
        try:
            stmt = select(WebhookSubscription.uuid).where(WebhookSubscription.uuid == domain_entity.uuid)
            result = await self._session.execute(stmt)
            if result.scalar_one_or_none() is not None:
                raise AlreadyExistsError(f"Подписка на webhook с UUID {domain_entity.uuid} уже существует")
        except AlreadyExistsError:
            raise
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при проверке существования подписки: {e}") from e

        subscription_model = to_persistence_model_subscription(domain_entity)

        try:
            self._session.add(subscription_model)
            await self._session.flush()
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при создании подписки на webhook: {e}") from e

        return to_domain_entity_subscription(subscription_model)

    async def update(self, domain_entity: WebhookSubscriptionEntity) -> WebhookSubscriptionEntity:
        """Обновляет существующую подписку на webhook"""
        subscription_model = await self._session.get(WebhookSubscription, domain_entity.uuid)
        if subscription_model is None:
            raise DoesNotExistError(f"Подписка на webhook с UUID {domain_entity.uuid} не найдена")

        updated_model = to_persistence_model_subscription(domain_entity)
        for key, value in updated_model.model_dump(exclude={"uuid", "created_at"}).items():
            setattr(subscription_model, key, value)

        try:
            await self._session.flush()
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при обновлении подписки на webhook: {e}") from e

        return to_domain_entity_subscription(subscription_model)

    async def delete(self, uuid: UUID) -> None:
        """Удаляет подписку на webhook по UUID"""
        try:
            subscription_model = await self._session.get(WebhookSubscription, uuid)
            if subscription_model is None:
                raise DoesNotExistError(f"Подписка на webhook с UUID {uuid} не найдена")
            await self._session.delete(subscription_model)
        except DoesNotExistError:
            raise
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при удалении подписки на webhook: {e}") from e
