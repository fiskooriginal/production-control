from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.common.events import DomainEvent


@dataclass(frozen=True)
class ReportGeneratedEvent(DomainEvent):
    batch_id: UUID
    report_type: str
    file_url: str
    expires_at: datetime
