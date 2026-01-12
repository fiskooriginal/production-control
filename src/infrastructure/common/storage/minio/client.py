from minio import Minio

from src.core.logging import get_logger
from src.core.settings import MinIOSettings
from src.infrastructure.common.storage.minio.impl import MinIOStorageServiceImpl

logger = get_logger("storage.minio")


async def init_minio_storage(minio_settings: MinIOSettings) -> MinIOStorageServiceImpl:
    """
    Инициализирует MinIO storage сервис и создает бакеты из настроек, если они не существуют.

    Args:
        minio_settings: Настройки MinIO

    Returns:
        Инициализированный storage сервис

    Raises:
        StorageConnectionError: При ошибке создания бакетов
    """
    try:
        minio_client = Minio(
            minio_settings.endpoint,
            access_key=minio_settings.access_key,
            secret_key=minio_settings.secret_key,
            secure=minio_settings.secure,
            region=minio_settings.region,
        )

        storage_service = MinIOStorageServiceImpl(minio_client, minio_settings)
        await storage_service.ensure_buckets()
        logger.info(f"MinIO storage initialized successfully (endpoint: {minio_settings.endpoint})")
        return storage_service
    except Exception as e:
        logger.error(f"Failed to initialize MinIO storage: {e}")
        raise
