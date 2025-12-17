from src.domain.shared.exceptions import DomainException


class WebhookSubscriptionInvalidUrlError(DomainException):
    """Исключение для невалидного формата URL"""

    def __init__(self, url: str) -> None:
        message = f"WebhookSubscriptionEntity.url: невалидный формат URL '{url}'. Ожидается http:// или https://"
        super().__init__(message)
        self.url = url


class WebhookSubscriptionInvalidEventsError(DomainException):
    """Исключение для невалидного списка событий"""

    def __init__(self, reason: str) -> None:
        message = f"WebhookSubscriptionEntity.events: {reason}"
        super().__init__(message)
        self.reason = reason
