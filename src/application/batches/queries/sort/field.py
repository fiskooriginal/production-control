from enum import Enum


class BatchSortField(str, Enum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    BATCH_NUMBER = "batch_number"
    BATCH_DATE = "batch_date"
    SHIFT = "shift"
    TEAM = "team"
    IS_CLOSED = "is_closed"
