import enum


class WebhookStatus(enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

    def __str__(self) -> str:
        return self.value
