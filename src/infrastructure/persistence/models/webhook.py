from uuid import UUID

from sqlalchemy import JSON, Column
from sqlalchemy import Enum as SQLEnum
from sqlmodel import Field, Relationship

from src.domain.webhooks.enums import WebhookEventType, WebhookStatus
from src.infrastructure.persistence.models.base import BaseModel


class WebhookSubscription(BaseModel, table=True):
    """Подписка на вебхуки с поддержкой событий"""

    __tablename__ = "webhook_subscriptions"

    url: str
    events: list[WebhookEventType] = Field(sa_column=Column(JSON))
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

    event_type: WebhookEventType = Field(sa_column=Column(SQLEnum(WebhookEventType)))
    status: WebhookStatus = Field(sa_column=Column(SQLEnum(WebhookStatus)))
    attempts: int = 0

    payload: dict = Field(sa_column=Column(JSON))
    response_status: int | None = None
    response_body: str | None = None
    error_message: str | None = None

    subscription_id: UUID = Field(
        foreign_key="webhook_subscriptions.uuid",
        sa_column_kwargs={"nullable": False},
    )

    # связи
    subscription: WebhookSubscription = Relationship(
        back_populates="deliveries",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
