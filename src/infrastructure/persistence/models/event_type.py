from sqlalchemy import Index
from sqlmodel import Field

from src.infrastructure.persistence.models.base import BaseModel


class EventType(BaseModel, table=True):
    """Модель типа события"""

    __tablename__ = "event_types"
    __table_args__ = (
        Index("idx_event_type_name", "name"),
        Index("idx_event_type_version", "version"),
    )

    name: str = Field(nullable=False, index=True, unique=True)
    version: int = Field(nullable=False, default=1, index=True)
    webhook_enabled: bool = Field(nullable=False, default=True)
    description: str | None = Field(default=None, nullable=True)
