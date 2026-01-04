import enum


class WebhookStatus(enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

    def __str__(self) -> str:
        return self.value


class WebhookEventType(enum.Enum):
    BATCH_CREATED = "batch_created"
    BATCH_CLOSED = "batch_closed"
    BATCH_OPENED = "batch_opened"
    BATCH_PRODUCT_ADDED = "batch_product_added"
    BATCH_PRODUCT_REMOVED = "batch_product_removed"
    BATCH_AGGREGATED = "batch_aggregated"
    BATCH_DELETED = "batch_deleted"
    BATCH_REPORT_GENERATED = "batch_report_generated"
    BATCH_IMPORT_COMPLETED = "batch_import_completed"
    PRODUCT_AGGREGATED = "product_aggregated"
    WORK_CENTER_DELETED = "work_center_deleted"

    def __str__(self) -> str:
        return self.value
