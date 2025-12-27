from src.domain.common.exceptions.base import DomainException


class InvalidStateError(DomainException):
    """Исключение для невалидных состояний сущности"""

    ...
