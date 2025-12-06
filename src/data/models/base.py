from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import MetaData
from sqlmodel import Field, SQLModel

from src.core.config import DB_SCHEMA

meta = MetaData(schema=DB_SCHEMA)


class BaseModel(SQLModel):
    """Базовая модель с UUID"""

    metadata = meta

    uuid: UUID = Field(primary_key=True, default_factory=uuid4, unique=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime | None = None
