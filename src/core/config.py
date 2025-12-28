from os import getenv as os_getenv
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env", override=True)


def getenv(key: str, default: str | None = None) -> str | None:
    """Получает значение переменной окружения и очищает его от пробелов и комментариев."""
    value = os_getenv(key, default)
    if not value:
        return None
    return value.strip() if not value.startswith("#") else value.split("#")[0].strip()


# Database settings
DB_HOST: str = getenv("DB_HOST", "postgres")
DB_PORT: str = getenv("DB_PORT", "5432")
DB_NAME: str = getenv("DB_NAME", "production_control")
DB_USER: str = getenv("DB_USER", "postgres")
DB_PASSWORD: str = getenv("DB_PASSWORD", "postgres")
DB_SCHEMA: str = getenv("DB_SCHEMA", "public")

# Redis settings
REDIS_HOST: str = getenv("REDIS_HOST", "localhost")
REDIS_PORT: str = getenv("REDIS_PORT", "6379")
REDIS_DB: str = getenv("REDIS_DB", "0")
REDIS_PASSWORD: str | None = getenv("REDIS_PASSWORD")

# Validation
TEXT_MAX_LENGTH: int | None = int(getenv("TEXT_MAX_LENGTH", "255"))

# Logging settings
LOG_LEVEL: str = getenv("LOG_LEVEL", "INFO")

# RabbitMQ settings
RABBITMQ_HOST: str = getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT: str = getenv("RABBITMQ_PORT", "5672")
RABBITMQ_USER: str = getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD: str = getenv("RABBITMQ_PASSWORD", "guest")
RABBITMQ_VHOST: str = getenv("RABBITMQ_VHOST", "/")

# Celery settings
CELERY_BROKER_URL: str | None = getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND: str | None = getenv("CELERY_RESULT_BACKEND")
CELERY_TIMEZONE: str = getenv("CELERY_TIMEZONE", "UTC")
CELERY_TASK_DEFAULT_QUEUE: str = getenv("CELERY_TASK_DEFAULT_QUEUE", "default")
CELERY_TASK_ACKS_LATE: bool = getenv("CELERY_TASK_ACKS_LATE", "true") == "true"
CELERY_TASK_REJECT_ON_WORKER_LOST: bool = getenv("CELERY_TASK_REJECT_ON_WORKER_LOST", "true") == "true"
CELERY_WORKER_CONCURRENCY: int = int(getenv("CELERY_WORKER_CONCURRENCY", "2"))
CELERY_REDIS_KEY_PREFIX: str = getenv("CELERY_REDIS_KEY_PREFIX", "celery")
CELERY_TASK_MAX_RETRIES: int = int(getenv("CELERY_TASK_MAX_RETRIES", "3"))
CELERY_TASK_DEFAULT_RETRY_DELAY: int = int(getenv("CELERY_TASK_DEFAULT_RETRY_DELAY", "60"))

# Cache settings
CACHE_ENABLED: bool = getenv("CACHE_ENABLED", "true") == "true"
CACHE_TTL_BATCH: int = int(getenv("CACHE_TTL_BATCH", "3600"))
CACHE_TTL_LIST: int = int(getenv("CACHE_TTL_LIST", "300"))
CACHE_KEY_PREFIX: str = getenv("CACHE_KEY_PREFIX", "cache")
