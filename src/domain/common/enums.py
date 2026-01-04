import enum


class EventTypesEnum(enum.Enum):
    """Enum для всех типов событий системы"""

    BATCH_CREATED = "batch.created"
    BATCH_CLOSED = "batch.closed"
    BATCH_OPENED = "batch.opened"
    BATCH_PRODUCT_ADDED = "batch.product_added"
    BATCH_PRODUCT_REMOVED = "batch.product_removed"
    BATCH_AGGREGATED = "batch.aggregated"
    BATCH_DELETED = "batch.deleted"
    BATCH_REPORT_GENERATED = "batch.report_generated"
    PRODUCT_AGGREGATED = "product.aggregated"
    WORK_CENTER_DELETED = "work_center.deleted"
    BATCH_IMPORT_COMPLETED = "batch.import_completed"

    def __str__(self) -> str:
        return self.value
