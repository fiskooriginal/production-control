from celery import Celery

from src.core.logging import get_logger
from src.core.settings import CelerySettings, RabbitMQSettings, RedisSettings
from src.infrastructure.celery.beat_schedule import beat_schedule

logger = get_logger("celery")

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
    include=["src.infrastructure.celery.tasks"],
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
