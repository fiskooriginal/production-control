from src.domain.common.exceptions.base import DomainException


class EmptyFieldError(DomainException):
    """Исключение для пустых обязательных полей"""

    ...
