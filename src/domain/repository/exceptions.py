from src.domain.shared.exceptions import DomainException


class RepositoryException(DomainException):
    """Базовое исключение для операций с репозиториями"""

    ...


class AlreadyExistsError(RepositoryException):
    """Исключение для случаев, когда сущность уже существует"""

    ...


class DoesNotExistError(RepositoryException):
    """Исключение для случаев, когда сущность не найдена"""

    ...


class MultipleFoundError(RepositoryException):
    """Исключение для случаев, когда найдено несколько сущностей вместо одной"""

    ...


class RepositoryOperationError(RepositoryException):
    """Исключение для ошибок операций с репозиторием"""

    ...
