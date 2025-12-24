from dataclasses import dataclass

from src.domain.shared.entities import BaseEntity
from src.domain.work_centers.value_objects import WorkCenterIdentifier, WorkCenterName


@dataclass(slots=True, kw_only=True)
class WorkCenterEntity(BaseEntity):
    identifier: WorkCenterIdentifier
    name: WorkCenterName
