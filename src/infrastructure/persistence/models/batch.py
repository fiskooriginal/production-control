from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Index
from sqlmodel import Field, Relationship

from src.infrastructure.persistence.models.base import BaseModel

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.product import Product
    from src.infrastructure.persistence.models.work_center import WorkCenter


class Batch(BaseModel, table=True):
    """Партия"""

    __tablename__ = "batches"
    __table_args__ = (
        Index("idx_batch_number", "batch_number"),
        Index("idx_batch_date", "batch_date"),
        Index("idx_batch_number_date", "batch_number", "batch_date"),
    )

    # статус партии
    is_closed: bool = False
    closed_at: datetime | None = None

    # описание задачи
    task_description: str
    work_center_id: UUID = Field(foreign_key="work_centers.uuid", sa_column_kwargs={"nullable": False})
    shift: str
    team: str

    # идентификатор партии
    batch_number: int
    batch_date: date

    # продукция
    nomenclature: str
    ekn_code: str

    # временные рамки смены
    shift_start_time: datetime
    shift_end_time: datetime

    work_center: "WorkCenter" = Relationship(
        back_populates="batches",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    products: list["Product"] = Relationship(
        back_populates="batch",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
