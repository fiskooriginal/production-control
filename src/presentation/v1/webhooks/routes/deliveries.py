from uuid import UUID

from fastapi import APIRouter, Depends

from src.presentation.v1.common.schemas import PaginationParams
from src.presentation.v1.webhooks.di.queries import list_webhook_deliveries
from src.presentation.v1.webhooks.mappers import (
    build_list_webhook_deliveries_query,
    delivery_entity_to_response,
)
from src.presentation.v1.webhooks.schemas import ListWebhookDeliveriesResponse

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.get("/{subscription_id}/deliveries", response_model=ListWebhookDeliveriesResponse)
async def list_webhook_deliveries(
    subscription_id: UUID,
    query_handler: list_webhook_deliveries,
    pagination_params: PaginationParams = Depends(),
) -> ListWebhookDeliveriesResponse:
    """
    Получает список доставок для подписки на webhook с пагинацией.
    """
    query = build_list_webhook_deliveries_query(subscription_id, pagination_params)
    result = await query_handler.execute(query)
    return ListWebhookDeliveriesResponse(
        items=[delivery_entity_to_response(delivery) for delivery in result.items],
        total=result.total,
        limit=result.limit,
        offset=result.offset,
    )
