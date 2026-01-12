from src.domain.common.exceptions.repositories.base import RepositoryException


class AlreadyExistsError(RepositoryException):
    """Исключение для случаев, когда сущность уже существует"""

    ...
