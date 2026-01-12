from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class WorkCenterReadFilters:
    identifier: str | None = None
