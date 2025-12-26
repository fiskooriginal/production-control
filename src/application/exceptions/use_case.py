from src.application.exceptions.base import ApplicationException


class UseCaseException(ApplicationException):
    """Исключение для ошибок выполнения use case"""

    ...


class ValidationException(ApplicationException):
    """Исключение для ошибок валидации на уровне приложения"""

    ...


class BusinessRuleViolationException(ApplicationException):
    """Исключение для нарушений бизнес-правил"""

    ...
