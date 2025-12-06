from dataclasses import dataclass

from src.core.config import (
    DB_HOST,
    DB_NAME,
    DB_PASSWORD,
    DB_PORT,
    DB_SCHEMA,
    DB_USER,
    REDIS_DB,
    REDIS_HOST,
    REDIS_PASSWORD,
    REDIS_PORT,
    REDIS_URL,
)


@dataclass
class DatabaseSettings:
    host: str = DB_HOST
    port: str = DB_PORT
    schema: str = DB_SCHEMA
    name: str = DB_NAME
    user: str = DB_USER
    password: str = DB_PASSWORD

    @property
    def url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}?schema={self.schema}"
        )


@dataclass
class RedisSettings:
    host: str = REDIS_HOST
    port: int = REDIS_PORT
    db: int = REDIS_DB
    password: str | None = REDIS_PASSWORD
    url: str | None = REDIS_URL

    def get_url(self) -> str:
        """Get Redis connection URL."""
        if self.url:
            return self.url
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"
