from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Relationship

from src.infrastructure.persistence.models.base import BaseModel

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.batch import Batch


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

    batches: list["Batch"] = Relationship(
        back_populates="work_center",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
