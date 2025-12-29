from src.infrastructure.common.exceptions.base import InfrastructureException


class EmailError(InfrastructureException):
    """Исключение для ошибок работы с email."""


class EmailConnectionError(EmailError):
    """Исключение для ошибок подключения к SMTP серверу."""


class EmailSendError(EmailError):
    """Исключение для ошибок отправки email."""


class EmailConfigurationError(EmailError):
    """Исключение для ошибок конфигурации email сервиса."""
