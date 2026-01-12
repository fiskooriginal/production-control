from io import BytesIO
from typing import Protocol

from src.application.common.storage.dtos import FileInfo


class StorageServiceProtocol(Protocol):
    """Протокол для сервиса хранения файлов в MinIO."""

    async def ensure_buckets(self) -> None:
        """
        Создаёт необходимые bucket'ы в хранилище. Список имён bucket'ов получается из переменных окружения.
        """
        ...

    async def upload_file(
        self,
        bucket_name: str,
        object_name: str,
        file_data: bytes | BytesIO,
        file_extension: str | None = None,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> str:
        """
        Загружает файл в хранилище.

        Args:
            bucket_name: Имя bucket'а в хранилище
            object_name: Имя объекта в хранилище
            file_data: Данные файла (bytes или BytesIO)
            file_extension: Расширение файла (например, pdf или .pdf, xlsx или .xlsx, etc.)
            content_type: MIME-тип файла (если None, определяется по расширению)
            metadata: Метаданные объекта

        Returns:
            Путь к загруженному объекту

        Raises:
            StorageError: При ошибке загрузки
        """
        ...

    async def download_file(self, bucket_name: str, object_name: str) -> bytes:
        """
        Скачивает файл из хранилища.

        Args:
            bucket_name: Имя bucket'а в хранилище
            object_name: Имя объекта в хранилище

        Returns:
            Данные файла

        Raises:
            StorageError: При ошибке скачивания
        """
        ...

    async def delete_file(self, bucket_name: str, object_name: str) -> None:
        """
        Удаляет файл из хранилища.

        Args:
            bucket_name: Имя bucket'а в хранилище
            object_name: Имя объекта в хранилище

        Raises:
            StorageError: При ошибке удаления
        """
        ...

    async def file_exists(self, bucket_name: str, object_name: str) -> bool:
        """
        Проверяет существование файла в хранилище.

        Args:
            bucket_name: Имя bucket'а в хранилище
            object_name: Имя объекта в хранилище

        Returns:
            True если файл существует, False иначе
        """
        ...

    async def get_presigned_url(self, bucket_name: str, object_name: str, expires_seconds: int = 3600) -> str:
        """
        Генерирует presigned URL для доступа к файлу.

        Args:
            bucket_name: Имя bucket'а в хранилище
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
        bucket_name: str,
        prefix: str | None = None,
        recursive: bool = True,
    ) -> list[FileInfo]:
        """
        Получает список всех файлов в bucket'е.

        Args:
            bucket_name: Имя bucket'а в хранилище
            prefix: Префикс для фильтрации файлов
            recursive: Рекурсивный поиск (включая подпапки)

        Returns:
            Список информации о файлах

        Raises:
            StorageError: При ошибке получения списка файлов
        """
        ...
