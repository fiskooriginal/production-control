from minio import Minio
from minio.error import S3Error

from src.core.logging import get_logger
from src.core.settings import MinIOSettings
from src.infrastructure.storage.exceptions import StorageConnectionError
from src.infrastructure.storage.minio import MinIOStorageServiceImpl

logger = get_logger("storage.minio")


def init_storage(minio_settings: MinIOSettings, bucket_name: str) -> MinIOStorageServiceImpl:
    """
    Инициализирует MinIO storage сервис.

    Args:
        minio_settings: Настройки MinIO
        bucket_name: Имя bucket'а для работы

    Returns:
        Инициализированный storage сервис

    Raises:
        StorageConnectionError: Если bucket не существует
    """
    try:
        minio_client = Minio(
            minio_settings.endpoint,
            access_key=minio_settings.access_key,
            secret_key=minio_settings.secret_key,
            secure=minio_settings.secure,
            region=minio_settings.region,
        )

        exists = minio_client.bucket_exists(bucket_name)
        if not exists:
            raise StorageConnectionError(
                f"Bucket '{bucket_name}' does not exist. Available buckets: {minio_settings.buckets}",
            )

        storage_service = MinIOStorageServiceImpl(minio_client, minio_settings, bucket_name)
        logger.info(
            f"MinIO storage initialized successfully (endpoint: {minio_settings.endpoint}, bucket: {bucket_name})",
        )
        return storage_service
    except S3Error as e:
        logger.error(f"Failed to check bucket existence: {e}")
        raise StorageConnectionError(f"Failed to check bucket existence: {e}") from e
    except Exception as e:
        logger.error(f"Failed to initialize MinIO storage: {e}")
        raise


async def init_storage_async(
    minio_settings: MinIOSettings,
    bucket_name: str,
) -> MinIOStorageServiceImpl:
    """
    Асинхронно инициализирует MinIO storage сервис.

    Args:
        minio_settings: Настройки MinIO
        bucket_name: Имя bucket'а для работы

    Returns:
        Инициализированный storage сервис

    Raises:
        StorageConnectionError: Если bucket не существует
    """
    try:
        minio_client = Minio(
            minio_settings.endpoint,
            access_key=minio_settings.access_key,
            secret_key=minio_settings.secret_key,
            secure=minio_settings.secure,
            region=minio_settings.region,
        )

        storage_service = MinIOStorageServiceImpl(minio_client, minio_settings, bucket_name)
        await storage_service._check_bucket_exists()
        logger.info(
            f"MinIO storage initialized successfully (endpoint: {minio_settings.endpoint}, bucket: {bucket_name})",
        )
        return storage_service
    except Exception as e:
        logger.error(f"Failed to initialize MinIO storage: {e}")
        raise
