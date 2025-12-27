from enum import Enum


class WorkCenterSortField(str, Enum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    IDENTIFIER = "identifier"
    NAME = "name"
