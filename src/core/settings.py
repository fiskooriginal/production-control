from dataclasses import dataclass

from src.core.config import (
    CACHE_ENABLED,
    CACHE_KEY_PREFIX,
    CACHE_TTL_BATCH,
    CACHE_TTL_LIST,
    CELERY_BROKER_URL,
    CELERY_REDIS_KEY_PREFIX,
    CELERY_RESULT_BACKEND,
    CELERY_TASK_ACKS_LATE,
    CELERY_TASK_DEFAULT_QUEUE,
    CELERY_TASK_DEFAULT_RETRY_DELAY,
    CELERY_TASK_MAX_RETRIES,
    CELERY_TASK_REJECT_ON_WORKER_LOST,
    CELERY_TIMEZONE,
    CELERY_WORKER_CONCURRENCY,
    DB_HOST,
    DB_NAME,
    DB_PASSWORD,
    DB_PORT,
    DB_SCHEMA,
    DB_USER,
    RABBITMQ_HOST,
    RABBITMQ_PASSWORD,
    RABBITMQ_PORT,
    RABBITMQ_USER,
    RABBITMQ_VHOST,
    REDIS_DB,
    REDIS_HOST,
    REDIS_PASSWORD,
    REDIS_PORT,
)


@dataclass
class DatabaseSettings:
    host: str = DB_HOST
    port: int = DB_PORT
    schema: str = DB_SCHEMA
    name: str = DB_NAME
    user: str = DB_USER
    password: str = DB_PASSWORD

    def __post_init__(self) -> None:
        if not self.host:
            raise ValueError("DB_HOST is not set")
        if not self.port:
            raise ValueError("DB_PORT is not set")
        if not self.name:
            raise ValueError("DB_NAME is not set")
        if not self.user:
            raise ValueError("DB_USER is not set")
        if not self.password:
            raise ValueError("DB_PASSWORD is not set")

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    def get_safe_url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:***@{self.host}:{self.port}/{self.name}"

    def __repr__(self) -> str:
        return (
            f"DatabaseSettings(host={self.host!r}, port={self.port}, "
            f"schema={self.schema!r}, name={self.name!r}, user={self.user!r}, password='***')"
        )


@dataclass
class RedisSettings:
    host: str = REDIS_HOST
    port: int = REDIS_PORT
    prefix: str = REDIS_DB
    password: str | None = REDIS_PASSWORD

    def get_url(self) -> str:
        """Get Redis connection URL."""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.prefix}"
        return f"redis://{self.host}:{self.port}/{self.prefix}"


@dataclass
class RabbitMQSettings:
    host: str = RABBITMQ_HOST
    port: int = RABBITMQ_PORT
    user: str = RABBITMQ_USER
    password: str = RABBITMQ_PASSWORD
    vhost: str = RABBITMQ_VHOST

    def get_broker_url(self) -> str:
        """Get RabbitMQ broker URL for Celery."""
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/{self.vhost}"


@dataclass
class CelerySettings:
    broker_url: str | None = CELERY_BROKER_URL
    result_backend: str | None = CELERY_RESULT_BACKEND
    timezone: str = CELERY_TIMEZONE
    task_default_queue: str = CELERY_TASK_DEFAULT_QUEUE
    task_acks_late: bool = CELERY_TASK_ACKS_LATE
    task_reject_on_worker_lost: bool = CELERY_TASK_REJECT_ON_WORKER_LOST
    worker_concurrency: int = CELERY_WORKER_CONCURRENCY
    redis_key_prefix: str = CELERY_REDIS_KEY_PREFIX
    task_max_retries: int = CELERY_TASK_MAX_RETRIES
    task_default_retry_delay: int = CELERY_TASK_DEFAULT_RETRY_DELAY

    def get_broker_url(self, rabbitmq_settings: RabbitMQSettings) -> str:
        """Get broker URL, use configured or build from RabbitMQ settings."""
        if self.broker_url and self.broker_url.strip():
            return self.broker_url.strip()
        return rabbitmq_settings.get_broker_url()

    def get_result_backend_url(self, redis_settings: RedisSettings) -> str:
        """Get result backend URL, use configured or build from Redis settings."""
        if self.result_backend and self.result_backend.strip():
            return self.result_backend.strip()
        return redis_settings.get_url()


@dataclass
class CacheSettings:
    enabled: bool = CACHE_ENABLED
    ttl_batch: int = CACHE_TTL_BATCH
    ttl_list: int = CACHE_TTL_LIST
    key_prefix: str = CACHE_KEY_PREFIX
