from dataclasses import dataclass

from src.application.products.queries.sort.field import ProductSortField
from src.domain.common.queries import SortDirection


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductSortSpec:
    field: ProductSortField
    direction: SortDirection = SortDirection.ASC
