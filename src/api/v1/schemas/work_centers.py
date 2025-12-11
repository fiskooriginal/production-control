from uuid import UUID

from pydantic import BaseModel

from src.api.v1.schemas.base import TimestampSchema, UUIDSchema
from src.api.v1.schemas.batches import BatchResponseSchema


class WorkCenterBaseSchema(BaseModel):
    identifier: str
    name: str
    author: UUID


class WorkCenterCreateUpdateSchema(WorkCenterBaseSchema): ...


class WorkCenterResponseSchema(WorkCenterBaseSchema, UUIDSchema, TimestampSchema):
    batches: list[BatchResponseSchema]
