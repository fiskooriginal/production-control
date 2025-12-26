from src.presentation.exceptions.base import PresentationException


class SerializationException(PresentationException):
    """Исключение для ошибок сериализации данных"""

    ...


class RequestValidationException(PresentationException):
    """Исключение для ошибок валидации запросов"""

    ...
