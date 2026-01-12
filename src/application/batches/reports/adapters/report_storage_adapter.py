from uuid import UUID

from src.application.batches.reports.dtos import ReportFormatEnum
from src.application.common.storage.interfaces import StorageServiceProtocol
from src.core.logging import get_logger

logger = get_logger("storage.reports")


class ReportStorageAdapter:
    """Адаптер для работы с отчетами через StorageServiceProtocol"""

    def __init__(self, storage_service: StorageServiceProtocol, bucket_name: str = "reports"):
        self._storage_service = storage_service
        self._bucket_name = bucket_name

    def _build_object_name(self, batch_id: UUID, format: ReportFormatEnum) -> str:
        """Формирует имя объекта в хранилище для отчета"""
        extension = format.value
        return f"{batch_id}/{extension}/report.{extension}"

    async def save_report(self, batch_id: UUID, content: bytes, format: ReportFormatEnum) -> str:
        """Сохраняет отчет и возвращает путь к файлу"""
        object_name = self._build_object_name(batch_id, format)

        logger.info(f"Saving report: batch_id={batch_id}, format={format.value}, object_name={object_name}")

        try:
            await self._storage_service.upload_file(
                bucket_name=self._bucket_name,
                object_name=object_name,
                file_data=content,
                file_extension=format.value,
            )

            logger.info(f"Report saved successfully: object_name={object_name}")
            return object_name
        except Exception as e:
            logger.exception(f"Failed to save report for batch {batch_id}: {e}")
            raise

    async def get_report_path(self, batch_id: UUID, format: ReportFormatEnum) -> str | None:
        """Получает путь к последнему отчету для партии и формата"""
        object_name = self._build_object_name(batch_id, format)

        logger.debug(
            f"Checking report existence: batch_id={batch_id}, format={format.value}, object_name={object_name}"
        )

        try:
            exists = await self._storage_service.file_exists(bucket_name=self._bucket_name, object_name=object_name)
            if exists:
                return object_name
            return None
        except Exception as e:
            logger.warning(f"Failed to check report existence for batch {batch_id}: {e}")
            return None

    async def delete_report(self, batch_id: UUID, format: ReportFormatEnum) -> None:
        """Удаляет отчет для партии и формата"""
        object_name = self._build_object_name(batch_id, format)

        logger.info(f"Deleting report: batch_id={batch_id}, format={format.value}, object_name={object_name}")

        try:
            await self._storage_service.delete_file(bucket_name=self._bucket_name, object_name=object_name)
            logger.info(f"Report deleted successfully: object_name={object_name}")
        except Exception as e:
            logger.exception(f"Failed to delete report for batch {batch_id}: {e}")
            raise

    async def get_presigned_url(self, object_name: str, expires_seconds: int = 3600) -> str:
        """Получает presigned URL для скачивания отчета"""
        logger.debug(f"Generating download URL for object: {object_name}")

        try:
            url = await self._storage_service.get_presigned_url(
                bucket_name=self._bucket_name, object_name=object_name, expires_seconds=expires_seconds
            )
            logger.debug(f"Download URL generated successfully for object: {object_name}")
            return url
        except Exception as e:
            logger.exception(f"Failed to generate download URL for object {object_name}: {e}")
            raise

    async def download_report(self, object_name: str) -> bytes:
        """Скачивает файл отчета из хранилища"""
        logger.debug(f"Downloading report: object_name={object_name}")

        try:
            content = await self._storage_service.download_file(bucket_name=self._bucket_name, object_name=object_name)
            logger.debug(f"Report downloaded successfully: object_name={object_name}")
            return content
        except Exception as e:
            logger.exception(f"Failed to download report for object {object_name}: {e}")
            raise
