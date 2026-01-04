from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, Column, Index
from sqlalchemy import Enum as SQLEnum
from sqlmodel import Field, Relationship

from src.domain.common.enums import EventTypesEnum
from src.domain.webhooks.enums import WebhookStatus
from src.infrastructure.persistence.models.base import BaseModel
from src.infrastructure.persistence.models.event_type import EventType


class WebhookSubscription(BaseModel, table=True):
    """Подписка на вебхуки с поддержкой событий"""

    __tablename__ = "webhook_subscriptions"

    url: str
    events: list[EventTypesEnum] = Field(sa_column=Column(JSON))
    secret_key: str
    is_active: bool = True
    retry_count: int = 3
    timeout_seconds: int = 10

    # связи
    deliveries: list["WebhookDelivery"] = Relationship(
        back_populates="subscription",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )


class WebhookDelivery(BaseModel, table=True):
    """Доставка вебхука"""

    __tablename__ = "webhook_deliveries"
    __table_args__ = (Index("idx_webhook_delivery_event_type_id", "event_type_id"),)

    event_type: str | None = Field(default=None, nullable=True)
    status: WebhookStatus = Field(sa_column=Column(SQLEnum(WebhookStatus)))
    attempts: int = 0

    payload: dict = Field(sa_column=Column(JSON))
    response_status: int | None = None
    response_body: str | None = None
    error_message: str | None = None
    delivered_at: datetime | None = None

    subscription_id: UUID = Field(
        foreign_key="webhook_subscriptions.uuid",
        sa_column_kwargs={"nullable": False},
    )

    event_type_id: UUID = Field(
        default=None,
        foreign_key="event_types.uuid",
        nullable=True,
        index=True,
    )

    # связи
    subscription: WebhookSubscription = Relationship(
        back_populates="deliveries",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    event_type_ref: EventType = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"},
    )
