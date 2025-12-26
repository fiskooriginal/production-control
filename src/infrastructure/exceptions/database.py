from src.infrastructure.exceptions.base import InfrastructureException


class DatabaseException(InfrastructureException):
    """Исключение для ошибок работы с базой данных"""

    ...


class ConnectionException(InfrastructureException):
    """Исключение для ошибок подключения к внешним сервисам"""

    ...


class MappingException(InfrastructureException):
    """Исключение для ошибок маппинга между доменными и persistence моделями"""

    ...


class OutboxRepositoryException(InfrastructureException):
    """Исключение для ошибок работы с outbox репозиторием"""

    ...
