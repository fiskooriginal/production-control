from dataclasses import dataclass
from io import BytesIO
from typing import Protocol


@dataclass
class FileInfo:
    """Информация о файле в хранилище."""

    name: str
    size: int
    last_modified: str
    etag: str | None = None


class StorageServiceProtocol(Protocol):
    """Протокол для сервиса хранения файлов в MinIO."""

    async def upload_file(
        self,
        object_name: str,
        file_data: bytes | BytesIO,
        file_extension: str | None = None,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> str:
        """
        Загружает файл в хранилище.

        Args:
            object_name: Имя объекта в хранилище
            file_data: Данные файла (bytes или BytesIO)
            file_extension: Расширение файла (например, "xlsx" или ".xlsx")
            content_type: MIME-тип файла (если None, определяется по расширению)
            metadata: Метаданные объекта

        Returns:
            Путь к загруженному объекту

        Raises:
            StorageError: При ошибке загрузки
        """
        ...

    async def download_file(self, object_name: str) -> bytes:
        """
        Скачивает файл из хранилища.

        Args:
            object_name: Имя объекта в хранилище

        Returns:
            Данные файла

        Raises:
            StorageError: При ошибке скачивания
        """
        ...

    async def delete_file(self, object_name: str) -> None:
        """
        Удаляет файл из хранилища.

        Args:
            object_name: Имя объекта в хранилище

        Raises:
            StorageError: При ошибке удаления
        """
        ...

    async def file_exists(self, object_name: str) -> bool:
        """
        Проверяет существование файла в хранилище.

        Args:
            object_name: Имя объекта в хранилище

        Returns:
            True если файл существует, False иначе
        """
        ...

    async def get_presigned_url(self, object_name: str, expires_seconds: int = 3600) -> str:
        """
        Генерирует presigned URL для доступа к файлу.

        Args:
            object_name: Имя объекта в хранилище
            expires_seconds: Время жизни URL в секундах

        Returns:
            Presigned URL

        Raises:
            StorageError: При ошибке генерации URL
        """
        ...

    async def list_files(
        self,
        prefix: str | None = None,
        recursive: bool = True,
    ) -> list[FileInfo]:
        """
        Получает список всех файлов в bucket'е.

        Args:
            prefix: Префикс для фильтрации файлов
            recursive: Рекурсивный поиск (включая подпапки)

        Returns:
            Список информации о файлах

        Raises:
            StorageError: При ошибке получения списка файлов
        """
        ...
