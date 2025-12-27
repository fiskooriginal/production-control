from os import getenv as os_getenv
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


def getenv(key: str, default: str | None = None) -> str | None:
    """Получает значение переменной окружения и очищает его от пробелов и комментариев."""
    value = os_getenv(key, default)
    if not value:
        return None
    return value.strip() if not value.startswith("#") else value.split("#")[0].strip()


# Database settings
DB_HOST: str = getenv("DB_HOST")
DB_PORT: int = int(getenv("DB_PORT"))
DB_NAME: str = getenv("DB_NAME")
DB_USER: str = getenv("DB_USER")
DB_PASSWORD: str = getenv("DB_PASSWORD")
DB_SCHEMA: str = getenv("DB_SCHEMA", "public")

# Redis settings
REDIS_HOST: str = getenv("REDIS_HOST", "localhost")
REDIS_PORT: int = int(getenv("REDIS_PORT", "6379"))
REDIS_PREFIX: str = getenv("REDIS_PREFIX", "0")
REDIS_PASSWORD: str | None = getenv("REDIS_PASSWORD")
REDIS_URL: str | None = getenv("REDIS_URL")

# Validation
TEXT_MAX_LENGTH: int | None = int(getenv("TEXT_MAX_LENGTH", "255"))

# Logging settings
LOG_LEVEL: str = getenv("LOG_LEVEL", "INFO")

# RabbitMQ settings
RABBITMQ_HOST: str = getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT: int = int(getenv("RABBITMQ_PORT", "5672"))
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
