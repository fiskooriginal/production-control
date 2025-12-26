from typing import Protocol
from uuid import UUID

from src.application.queries.batches import BatchReadDTO, ListBatchesQuery
from src.application.queries.products import ListProductsQuery, ProductReadDTO
from src.application.queries.work_centers import ListWorkCentersQuery, WorkCenterReadDTO
from src.domain.shared.queries import QueryResult


class BatchQueryServiceProtocol(Protocol):
    async def get(self, batch_id: UUID) -> BatchReadDTO | None:
        """Получает партию по UUID"""
        ...

    async def list(self, query: ListBatchesQuery) -> QueryResult[BatchReadDTO]:
        """Получает список партий с фильтрацией, пагинацией и сортировкой"""
        ...


class WorkCenterQueryServiceProtocol(Protocol):
    async def get(self, work_center_id: UUID) -> WorkCenterReadDTO | None:
        """Получает рабочий центр по UUID"""
        ...

    async def list(self, query: ListWorkCentersQuery) -> QueryResult[WorkCenterReadDTO]:
        """Получает список рабочих центров с фильтрацией, пагинацией и сортировкой"""
        ...


class ProductQueryServiceProtocol(Protocol):
    async def get(self, product_id: UUID) -> ProductReadDTO | None:
        """Получает продукт по UUID"""
        ...

    async def list(self, query: ListProductsQuery) -> QueryResult[ProductReadDTO]:
        """Получает список продуктов с пагинацией и сортировкой"""
        ...
