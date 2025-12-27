from enum import Enum


class ProductSortField(str, Enum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    UNIQUE_CODE = "unique_code"
    IS_AGGREGATED = "is_aggregated"
    AGGREGATED_AT = "aggregated_at"
