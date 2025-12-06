from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Relationship

from src.data.models.base import BaseModel

if TYPE_CHECKING:
    from src.data.models.batch import Batch


class WorkCenter(BaseModel, table=True):
    """Рабочий центр"""

    __tablename__ = "work_centers"
    __table_args__ = (
        UniqueConstraint("identifier", name="uq_work_center_identifier"),
        Index("idx_work_center_identifier", "identifier"),
    )

    identifier: str
    name: str
    author: UUID

    # связи
    batches: list["Batch"] = Relationship(back_populates="work_center")
