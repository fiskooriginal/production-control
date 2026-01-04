from datetime import datetime

from sqlmodel import Field, SQLModel

from src.core.time import datetime_now
from src.infrastructure.persistence.models.base import meta


class EventType(SQLModel, table=True):
    """Модель типа события для унифицированного хранилища"""

    __tablename__ = "event_types"
    metadata = meta

    event_name: str = Field(primary_key=True, unique=True, nullable=False)
    event_version: int = Field(default=1, nullable=False)
    description: str | None = Field(default=None, nullable=True)
    is_webhook_enabled: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime_now, nullable=False)
    updated_at: datetime | None = Field(default=None, nullable=True)
