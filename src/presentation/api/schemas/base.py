from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UUIDSchema(BaseModel):
    uuid: UUID


class TimestampSchema(BaseModel):
    created_at: datetime
    updated_at: datetime | None = None
