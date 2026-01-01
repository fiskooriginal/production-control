import asyncio

from celery import Celery
from celery.signals import worker_process_init, worker_process_shutdown
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.application.common.storage.interface import StorageServiceProtocol
from src.core.database import dispose_engine, init_engine, make_session_factory
from src.core.logging import get_logger
from src.core.settings import CelerySettings, DatabaseSettings, MinIOSettings, RabbitMQSettings, RedisSettings
from src.infrastructure.background_tasks.beat_schedule import beat_schedule
from src.infrastructure.common.storage.minio import init_minio_storage

logger = get_logger("celery")

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None
_worker_loop: asyncio.AbstractEventLoop | None = None
_storage_service: StorageServiceProtocol | None = None

rabbitmq_settings = RabbitMQSettings()
redis_settings = RedisSettings()
celery_settings = CelerySettings()

broker_url = celery_settings.get_broker_url(rabbitmq_settings)
result_backend = celery_settings.get_result_backend_url(redis_settings)

logger.info(f"Initializing Celery with broker: {broker_url}")
logger.info(f"Result backend: {result_backend}")

celery_app = Celery(
    "production_control",
    broker=broker_url,
    backend=result_backend,
    include=[
        "src.infrastructure.background_tasks.tasks.aggregate_batch",
        "src.infrastructure.background_tasks.tasks.process_outbox_events",
    ],
)

celery_app.conf.update(
    timezone=celery_settings.timezone,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_default_queue=celery_settings.task_default_queue,
    task_acks_late=celery_settings.task_acks_late,
    task_reject_on_worker_lost=celery_settings.task_reject_on_worker_lost,
    worker_concurrency=celery_settings.worker_concurrency,
    beat_schedule=beat_schedule,
)

logger.info(f"Celery app initialized successfully with {len(beat_schedule)} scheduled task(s)")


@worker_process_init.connect
def init_worker_db(**kwargs) -> None:
    """Инициализирует ресурсы при старте worker процесса"""
    global _engine, _session_factory, _worker_loop, _storage_service
    try:
        _worker_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_worker_loop)
        logger.info("Event loop created for worker")

        db_settings = DatabaseSettings()
        logger.info(f"Initializing database engine for worker: {db_settings.get_safe_url()}")
        _engine = init_engine(db_settings.url)
        _session_factory = make_session_factory(_engine)
        logger.info("Database engine initialized for worker")

        minio_settings = MinIOSettings()
        logger.info(f"Initializing MinIO storage for worker: endpoint={minio_settings.endpoint}")
        _storage_service = _worker_loop.run_until_complete(init_minio_storage(minio_settings))
        logger.info("MinIO storage initialized for worker")
    except Exception as e:
        logger.exception(f"Failed to initialize worker resources: {e}")
        raise


@worker_process_shutdown.connect
def shutdown_worker_db(**kwargs) -> None:
    """Корректно закрывает database engine и storage service при остановке worker процесса"""
    global _engine, _session_factory, _worker_loop, _storage_service
    if _engine and _worker_loop:
        try:
            logger.info("Disposing worker resources")
            _worker_loop.run_until_complete(dispose_engine(_engine))
            _engine = None
            _session_factory = None
            _storage_service = None
            _worker_loop.close()
            _worker_loop = None
            asyncio.set_event_loop(None)
            logger.info("Worker resources disposed")
        except Exception as e:
            logger.exception(f"Error disposing worker resources: {e}")


def get_engine() -> AsyncEngine:
    """Возвращает глобальный database engine для использования в задачах"""
    if _engine is None:
        raise RuntimeError("Database engine not initialized. Ensure worker_process_init signal was called.")
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Возвращает session factory для использования в задачах"""
    if _session_factory is None:
        raise RuntimeError("Session factory not initialized. Ensure worker_process_init signal was called.")
    return _session_factory


def get_storage_service() -> StorageServiceProtocol:
    """Возвращает глобальный storage service для использования в задачах"""
    if _storage_service is None:
        raise RuntimeError("Storage service not initialized. Ensure worker_process_init signal was called.")
    return _storage_service


def run_async_task(coro):
    """
    Запускает async задачу в глобальном event loop worker процесса.

    Использует один и тот же event loop для всех задач, чтобы избежать
    конфликтов с соединениями из пула SQLAlchemy.
    """
    global _worker_loop
    if _worker_loop is None:
        raise RuntimeError("Worker event loop not initialized. Ensure worker_process_init signal was called.")
    return _worker_loop.run_until_complete(coro)
