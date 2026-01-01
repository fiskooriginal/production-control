import asyncio

from datetime import timedelta
from io import BytesIO
from pathlib import Path

from minio import Minio
from minio.error import S3Error

from src.application.common.storage.interface import FileInfo, StorageServiceProtocol
from src.core.logging import get_logger
from src.core.settings import MinIOSettings
from src.infrastructure.common.storage.exceptions import (
    StorageConnectionError,
    StorageDeleteError,
    StorageDownloadError,
    StorageNotFoundError,
    StorageUploadError,
)
from src.infrastructure.common.storage.utils import get_content_type

logger = get_logger("storage.minio")


class MinIOStorageServiceImpl(StorageServiceProtocol):
    """Сервис для работы с MinIO хранилищем."""

    def __init__(self, minio_client: Minio, minio_settings: MinIOSettings):
        self._client = minio_client
        self._settings = minio_settings

    async def ensure_buckets(self) -> None:
        """Создает бакеты из настроек, если они не существуют."""

        if not self._settings.buckets:
            logger.warning("No buckets specified in settings")
            return

        for bucket_name in self._settings.buckets:
            try:
                exists = await asyncio.to_thread(self._client.bucket_exists, bucket_name)
                if not exists:
                    location = self._settings.region or "us-east-1"
                    await asyncio.to_thread(self._client.make_bucket, bucket_name, location)
                    logger.info(f"Created bucket '{bucket_name}' in region '{location}'")
                else:
                    logger.debug(f"Bucket '{bucket_name}' already exists")
            except S3Error as e:
                logger.error(f"Failed to check/create bucket '{bucket_name}': {e}")
                raise StorageConnectionError(f"Failed to ensure bucket '{bucket_name}': {e}") from e

    async def _check_bucket_exists(self, bucket_name: str) -> None:
        """Проверяет существование bucket и выбрасывает ошибку, если его нет."""
        try:
            exists = await asyncio.to_thread(self._client.bucket_exists, bucket_name)
            if not exists:
                raise StorageConnectionError(
                    f"Bucket '{bucket_name}' does not exist. Available buckets: {self._settings.buckets}"
                )
        except S3Error as e:
            logger.error(f"Failed to check bucket existence: {e}")
            raise StorageConnectionError(f"Failed to check bucket existence: {e}") from e

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
            StorageUploadError: При ошибке загрузки
        """

        try:
            if isinstance(file_data, bytes):
                data_stream = BytesIO(file_data)
                length = len(file_data)
            else:
                data_stream = file_data
                data_stream.seek(0, 2)
                length = data_stream.tell()
                data_stream.seek(0)

            if content_type is None:
                if file_extension is None:
                    file_extension = Path(object_name).suffix
                content_type = get_content_type(file_extension)

            result = await asyncio.to_thread(
                self._client.put_object,
                bucket_name,
                object_name,
                data_stream,
                length,
                content_type=content_type,
                metadata=metadata,
            )

            logger.info(f"Uploaded file: {object_name} (etag: {result.etag})")
            return object_name
        except S3Error as e:
            logger.error(f"Failed to upload file {object_name}: {e}")
            raise StorageUploadError(f"Failed to upload file {object_name}: {e}") from e

    async def download_file(self, bucket_name: str, object_name: str) -> bytes:
        """
        Скачивает файл из хранилища.

        Args:
            bucket_name: Имя bucket'а в хранилище
            object_name: Имя объекта в хранилище

        Returns:
            Данные файла

        Raises:
            StorageDownloadError: При ошибке скачивания
            StorageNotFoundError: Если файл не найден
        """
        try:
            response = await asyncio.to_thread(
                self._client.get_object,
                bucket_name,
                object_name,
            )

            try:
                data = await asyncio.to_thread(response.read)
                logger.info(f"Downloaded file: {object_name} ({len(data)} bytes)")
                return data
            finally:
                response.close()
                response.release_conn()
        except S3Error as e:
            if e.code == "NoSuchKey":
                logger.warning(f"File not found: {object_name}")
                raise StorageNotFoundError(f"File not found: {object_name}") from e
            logger.error(f"Failed to download file {object_name}: {e}")
            raise StorageDownloadError(f"Failed to download file {object_name}: {e}") from e

    async def delete_file(self, bucket_name: str, object_name: str) -> None:
        """
        Удаляет файл из хранилища.

        Args:
            bucket_name: Имя bucket'а в хранилище
            object_name: Имя объекта в хранилище

        Raises:
            StorageDeleteError: При ошибке удаления
        """
        try:
            await asyncio.to_thread(
                self._client.remove_object,
                bucket_name,
                object_name,
            )
            logger.info(f"Deleted file: {object_name}")
        except S3Error as e:
            logger.error(f"Failed to delete file {object_name}: {e}")
            raise StorageDeleteError(f"Failed to delete file {object_name}: {e}") from e

    async def file_exists(self, bucket_name: str, object_name: str) -> bool:
        """
        Проверяет существование файла в хранилище.

        Args:
            bucket_name: Имя bucket'а в хранилище
            object_name: Имя объекта в хранилище

        Returns:
            True если файл существует, False иначе
        """
        try:
            await asyncio.to_thread(
                self._client.stat_object,
                bucket_name,
                object_name,
            )
            return True
        except S3Error as e:
            if e.code == "NoSuchKey":
                return False
            logger.warning(f"Error checking file existence {object_name}: {e}")
            return False

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
        try:
            url = await asyncio.to_thread(
                self._client.presigned_get_object,
                bucket_name,
                object_name,
                expires=timedelta(seconds=expires_seconds),
            )
            logger.debug(f"Generated presigned URL for {object_name}")
            return url
        except S3Error as e:
            logger.error(f"Failed to generate presigned URL for {object_name}: {e}")
            raise StorageDownloadError(
                f"Failed to generate presigned URL for {object_name}: {e}",
            ) from e

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
        try:
            objects = await asyncio.to_thread(
                self._client.list_objects,
                bucket_name,
                prefix=prefix,
                recursive=recursive,
            )

            files = []
            for obj in objects:
                files.append(
                    FileInfo(
                        name=obj.object_name,
                        size=obj.size,
                        last_modified=obj.last_modified.isoformat() if obj.last_modified else "",
                        etag=obj.etag,
                    ),
                )

            logger.debug(f"Listed {len(files)} files from bucket {bucket_name}")
            return files
        except S3Error as e:
            logger.error(f"Failed to list files from bucket {bucket_name}: {e}")
            raise StorageDownloadError(
                f"Failed to list files from bucket {bucket_name}: {e}",
            ) from e
