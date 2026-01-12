from src.domain.common.exceptions.repositories.base import RepositoryException


class DoesNotExistError(RepositoryException):
    """Исключение для случаев, когда сущность не найдена"""

    ...
