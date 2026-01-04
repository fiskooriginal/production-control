from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.webhooks.queries.delivery import WebhookDeliveryQueryServiceProtocol
from src.application.webhooks.queries.queries import ListWebhookDeliveriesQuery
from src.domain.common.queries import QueryResult
from src.domain.webhooks.entities.delivery import WebhookDeliveryEntity
from src.infrastructure.common.exceptions import DatabaseException
from src.infrastructure.persistence.mappers.webhooks.delivery import to_domain_entity_delivery
from src.infrastructure.persistence.models.webhook import WebhookDelivery


class WebhookDeliveryQueryService(WebhookDeliveryQueryServiceProtocol):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_subscription_id(self, query: ListWebhookDeliveriesQuery) -> QueryResult[WebhookDeliveryEntity]:
        """Получает список доставок для подписки с пагинацией"""
        try:
            stmt = select(WebhookDelivery).where(WebhookDelivery.subscription_id == query.subscription_id)
            count_stmt = select(WebhookDelivery).where(WebhookDelivery.subscription_id == query.subscription_id)

            total_result = await self._session.execute(select(func.count()).select_from(count_stmt.subquery()))
            total = total_result.scalar_one() or 0

            if query.pagination:
                stmt = stmt.offset(query.pagination.offset).limit(query.pagination.limit)

            result = await self._session.execute(stmt)
            delivery_models = result.scalars().all()

            entities = [to_domain_entity_delivery(delivery) for delivery in delivery_models]

            return QueryResult[WebhookDeliveryEntity](
                items=entities,
                total=total,
                limit=query.pagination.limit if query.pagination else None,
                offset=query.pagination.offset if query.pagination else None,
            )
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении доставок webhook: {e}") from e
