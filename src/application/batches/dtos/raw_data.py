from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductRawDataDTO:
    """
    DTO для описания RawData у Products при экспорте и импорте.
    """

    unique_code: str
    batch_id: UUID
    is_aggregated: bool
    aggregated_at: datetime | None

    uuid: UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class BatchRawDataDTO:
    """
    DTO для описания RawData у Batches при экспорте и импорте.

    Содержит все поля, которые могут быть в файле экспорта/импорта.
    Некоторые поля опциональны, так как они присутствуют только при экспорте
    или при импорте существующих записей.
    """

    batch_number: int
    batch_date: date
    nomenclature: str
    ekn_code: str
    shift: str
    team: str
    task_description: str
    shift_start: datetime
    shift_end: datetime
    work_center_identifier: str
    work_center_name: str

    products: str  # JSON строка со списком ProductRawDataDTO

    uuid: UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    is_closed: bool | None = None
    closed_at: datetime | None = None
