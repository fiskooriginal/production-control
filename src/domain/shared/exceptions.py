class DomainException(Exception):
    """Базовое исключение для доменных ошибок"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


# Entity exceptions
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


# Repository exceptions
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
