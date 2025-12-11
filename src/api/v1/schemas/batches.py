from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from src.api.v1.schemas.base import TimestampSchema, UUIDSchema
from src.api.v1.schemas.products import ProductResponseSchema


class BatchBaseSchema(BaseModel):
    is_closed: bool
    batch_number: int
    batch_date: date
    task_description: str
    work_center_id: UUID
    shift: str
    team: str
    nomenclature: str
    ekn_code: str
    shift_start_time: datetime
    shift_end_time: datetime


class BatchCreateUpdateSchema(BatchBaseSchema): ...


class BatchResponseSchema(BatchBaseSchema, UUIDSchema, TimestampSchema):
    products: list[ProductResponseSchema]
