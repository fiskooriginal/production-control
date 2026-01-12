from src.domain.common.exceptions.repositories.base import RepositoryException


class MultipleFoundError(RepositoryException):
    """Исключение для случаев, когда найдено несколько сущностей вместо одной"""

    ...
