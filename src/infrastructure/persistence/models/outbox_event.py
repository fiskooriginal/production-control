from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import JSON, Index
from sqlmodel import Column, Field

from src.infrastructure.persistence.models.base import BaseModel


class OutboxEventStatusEnum(str, Enum):
    """Статус события в outbox"""

    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class OutboxEvent(BaseModel, table=True):
    """Transactional Outbox для доменных событий"""

    __tablename__ = "outbox_events"
    __table_args__ = (
        Index("idx_outbox_event_name", "event_name"),
        Index("idx_outbox_aggregate_id", "aggregate_id"),
        Index("idx_outbox_status", "status"),
        Index("idx_outbox_created_at", "created_at"),
        Index("idx_outbox_status_locked", "status", "locked_until"),
    )

    event_name: str = Field(nullable=False, index=True)
    event_version: int = Field(nullable=False, default=1)
    aggregate_id: UUID = Field(nullable=False, index=True)
    payload: dict = Field(sa_column=Column(JSON, nullable=False))
    occurred_at: datetime = Field(nullable=False)
    status: OutboxEventStatusEnum = Field(default=OutboxEventStatusEnum.PENDING, nullable=False)
    attempts: int = Field(default=0, nullable=False)
    locked_until: datetime | None = Field(default=None, nullable=True)
    processed_at: datetime | None = Field(default=None, nullable=True)
    last_error: str | None = Field(default=None, nullable=True)
    correlation_id: UUID | None = Field(default=None, nullable=True)
    causation_id: UUID | None = Field(default=None, nullable=True)
    event_metadata: dict | None = Field(default=None, sa_column=Column(JSON, nullable=True))
    dedup_key: str | None = Field(default=None, nullable=True, unique=True)
