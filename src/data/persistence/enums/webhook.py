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

    def __str__(self) -> str:
        return self.value
