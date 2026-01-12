from uuid import UUID

from sqlalchemy import cast, func, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.webhooks.queries.queries import ListWebhookSubscriptionsQuery
from src.application.webhooks.queries.subscription import WebhookSubscriptionQueryServiceProtocol
from src.domain.common.queries import QueryResult
from src.domain.webhooks.entities.subscription import WebhookSubscriptionEntity
from src.infrastructure.common.exceptions import DatabaseException
from src.infrastructure.persistence.mappers.webhooks.subscription import to_domain_entity
from src.infrastructure.persistence.models.webhook import WebhookSubscription


class WebhookSubscriptionQueryService(WebhookSubscriptionQueryServiceProtocol):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, subscription_id: UUID) -> WebhookSubscriptionEntity | None:
        """Получает подписку на webhook по UUID"""
        try:
            stmt = select(WebhookSubscription).where(WebhookSubscription.uuid == subscription_id)
            result = await self._session.execute(stmt)
            subscription_model = result.scalar_one_or_none()
            if subscription_model is None:
                return None
            return to_domain_entity(subscription_model)
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении подписки на webhook: {e}") from e

    async def list(self, query: ListWebhookSubscriptionsQuery) -> QueryResult[WebhookSubscriptionEntity]:
        """Получает список всех подписок на webhook с пагинацией"""
        try:
            stmt = select(WebhookSubscription)
            count_stmt = select(WebhookSubscription)

            if query.filters:
                stmt, count_stmt = self._apply_filters(stmt, count_stmt, query.filters)

            total_result = await self._session.execute(select(func.count()).select_from(count_stmt.subquery()))
            total = total_result.scalar_one() or 0

            if query.pagination:
                stmt = stmt.offset(query.pagination.offset).limit(query.pagination.limit)

            result = await self._session.execute(stmt)
            subscription_models = result.scalars().all()

            entities = [to_domain_entity(subscription) for subscription in subscription_models]

            return QueryResult[WebhookSubscriptionEntity](
                items=entities,
                total=total,
                limit=query.pagination.limit if query.pagination else None,
                offset=query.pagination.offset if query.pagination else None,
            )
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении списка подписок на webhook: {e}") from e

    def _apply_filters(self, stmt, count_stmt, filters):
        """Применяет фильтры к запросу"""
        from src.application.webhooks.queries.filters import WebhookReadFilters

        if not isinstance(filters, WebhookReadFilters):
            raise ValueError("filters должен быть типа WebhookReadFilters")

        if filters.event_type is not None:
            event_type_value = str(filters.event_type)
            events_jsonb = cast(WebhookSubscription.events, JSONB)
            filter_array = func.jsonb_build_array(event_type_value)
            stmt = stmt.where(events_jsonb.op("@>")(filter_array))
            count_stmt = count_stmt.where(events_jsonb.op("@>")(filter_array))

        return stmt, count_stmt
