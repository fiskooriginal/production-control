from os import getenv
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

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
