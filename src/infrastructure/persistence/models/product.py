from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field, Relationship

from src.infrastructure.persistence.models.base import BaseModel

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.batch import Batch


class Product(BaseModel, table=True):
    """Продукция"""

    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("unique_code", name="uq_product_unique_code"),
        Index("idx_product_unique_code", "unique_code"),
        Index("idx_product_batch_id", "batch_id"),
        Index("idx_product_is_aggregated", "is_aggregated"),
    )

    unique_code: str
    batch_id: UUID = Field(foreign_key="batches.uuid", sa_column_kwargs={"nullable": False})

    is_aggregated: bool = False
    aggregated_at: datetime | None = None

    batch: "Batch" = Relationship(
        back_populates="products",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
