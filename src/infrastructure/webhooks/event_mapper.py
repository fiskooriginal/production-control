from src.domain.webhooks.enums import WebhookEventType

EVENT_NAME_TO_WEBHOOK_TYPE: dict[str, WebhookEventType] = {
    "batch.created": WebhookEventType.BATCH_CREATED,
    "batch.closed": WebhookEventType.BATCH_CLOSED,
    "batch.opened": WebhookEventType.BATCH_OPENED,
    "batch.product_added": WebhookEventType.BATCH_PRODUCT_ADDED,
    "batch.product_removed": WebhookEventType.BATCH_PRODUCT_REMOVED,
    "batch.aggregated": WebhookEventType.BATCH_AGGREGATED,
    "batch.deleted": WebhookEventType.BATCH_DELETED,
    "batch.report_generated": WebhookEventType.BATCH_REPORT_GENERATED,
    "batch.import_completed": WebhookEventType.BATCH_IMPORT_COMPLETED,
    "product.aggregated": WebhookEventType.PRODUCT_AGGREGATED,
    "work_center.deleted": WebhookEventType.WORK_CENTER_DELETED,
}


def get_webhook_event_type(event_name: str) -> WebhookEventType | None:
    """
    Преобразует event_name из EventRegistry в WebhookEventType.
    Возвращает None, если событие не поддерживается webhooks.
    """
    return EVENT_NAME_TO_WEBHOOK_TYPE.get(event_name)
