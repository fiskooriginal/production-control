from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateWorkCenterInputDTO:
    identifier: str
    name: str
