class DomainException(Exception):
    """Базовое исключение для доменных ошибок"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class EmptyFieldError(DomainException):
    """Исключение для пустых обязательных полей"""

    ...


class InvalidValueError(DomainException):
    """Исключение для невалидных значений полей"""

    ...


class InvalidDateRangeError(DomainException):
    """Исключение для невалидных диапазонов дат"""

    ...


class InvalidStateError(DomainException):
    """Исключение для невалидных состояний сущности"""

    ...
