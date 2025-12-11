from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.api.v1.schemas.base import TimestampSchema, UUIDSchema


class ProductBaseSchema(BaseModel):
    unique_code: str
    batch_id: UUID
    is_aggregated: bool = False
    aggregated_at: datetime | None = None


class ProductCreateUpdateSchema(ProductBaseSchema): ...


class ProductResponseSchema(ProductBaseSchema, UUIDSchema, TimestampSchema): ...
