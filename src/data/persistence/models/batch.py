from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Index
from sqlmodel import Field, Relationship

from src.data.persistence.models.base import BaseModel

if TYPE_CHECKING:
    from src.data.persistence.models.product import Product
    from src.data.persistence.models.work_center import WorkCenter


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
    work_center_id: UUID = Field(foreign_key="work_centers.uuid")
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

    # связи
    work_center: "WorkCenter" = Relationship(back_populates="batches")
    products: list["Product"] = Relationship(back_populates="batch")
