from dataclasses import dataclass

from src.application.products.queries.sort import ProductSortSpec
from src.domain.common.queries import PaginationSpec


@dataclass(frozen=True, slots=True, kw_only=True)
class ListProductsQuery:
    pagination: PaginationSpec | None = None
    sort: ProductSortSpec | None = None
