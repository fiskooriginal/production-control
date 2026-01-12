from datetime import datetime, timedelta

from src.core.logging import get_logger
from src.core.settings import MinIOSettings
from src.core.time import datetime_now
from src.infrastructure.background_tasks.app import celery_app, get_storage_service, run_async_task

logger = get_logger("celery.tasks.cleanup_old_minio_files")


@celery_app.task(name="tasks.cleanup_old_minio_files")
def cleanup_old_minio_files() -> dict:
    """
    Удаляет файлы старше заданного количества дней из MinIO.

    Запускается: каждый день в 02:00

    Returns:
        {
            "success": True,
            "total_buckets": 3,
            "total_deleted": 15,
            "errors": 0
        }
    """
    return run_async_task(_cleanup_old_files_async())


async def _cleanup_old_files_async() -> dict:
    """Асинхронная часть задачи очистки старых файлов"""

    minio_settings = MinIOSettings()
    storage_service = get_storage_service()

    cutoff_date = datetime_now() - timedelta(days=minio_settings.files_lifetime_days)
    logger.info(
        f"Starting cleanup of files older than {minio_settings.files_lifetime_days} days (before {cutoff_date.isoformat()})"
    )

    total_deleted = 0
    total_errors = 0
    buckets_processed = 0

    if not minio_settings.buckets:
        logger.warning("No buckets configured for cleanup")
        return {
            "success": True,
            "total_buckets": 0,
            "total_deleted": 0,
            "errors": 0,
        }

    for bucket_name in minio_settings.buckets:
        try:
            logger.info(f"Processing bucket: {bucket_name}")

            files = await storage_service.list_files(bucket_name, recursive=True)

            old_files = []
            for file_info in files:
                try:
                    if file_info.last_modified:
                        file_date = datetime.fromisoformat(file_info.last_modified.replace("Z", "+00:00"))

                        if file_date.replace(tzinfo=None) < cutoff_date.replace(tzinfo=None):
                            old_files.append(file_info)
                except (ValueError, TypeError, AttributeError) as e:
                    logger.warning(f"Failed to parse last_modified for file {file_info.name}: {e}")
                    continue

            deleted_count = 0
            error_count = 0

            for file_info in old_files:
                try:
                    await storage_service.delete_file(bucket_name, file_info.name)
                    deleted_count += 1
                    logger.debug(f"Deleted file: {bucket_name}/{file_info.name}")
                except Exception as e:
                    error_count += 1
                    logger.error(f"Failed to delete file {bucket_name}/{file_info.name}: {e}")

            total_deleted += deleted_count
            total_errors += error_count
            buckets_processed += 1

            logger.info(
                f"Bucket {bucket_name}: deleted {deleted_count} files, errors: {error_count}, "
                f"total files checked: {len(files)}"
            )

        except Exception as e:
            total_errors += 1
            logger.exception(f"Failed to process bucket {bucket_name}: {e}")

    logger.info(
        f"Cleanup completed: processed {buckets_processed} buckets, "
        f"deleted {total_deleted} files, errors: {total_errors}"
    )

    return {
        "success": True,
        "total_buckets": buckets_processed,
        "total_deleted": total_deleted,
        "errors": total_errors,
    }
