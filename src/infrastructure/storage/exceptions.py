from src.infrastructure.common.exceptions.base import InfrastructureException


class StorageError(InfrastructureException):
    """Исключение для ошибок работы с хранилищем."""


class StorageConnectionError(StorageError):
    """Исключение для ошибок подключения к хранилищу."""


class StorageNotFoundError(StorageError):
    """Исключение для случая, когда объект не найден в хранилище."""


class StorageUploadError(StorageError):
    """Исключение для ошибок загрузки файла в хранилище."""


class StorageDownloadError(StorageError):
    """Исключение для ошибок скачивания файла из хранилища."""


class StorageDeleteError(StorageError):
    """Исключение для ошибок удаления файла из хранилища."""
