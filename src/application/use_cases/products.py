from datetime import datetime
from uuid import UUID

from src.data.persistence.repositories.products import ProductRepository
from src.domain.products.entities import ProductEntity
from src.domain.shared.exceptions import InvalidStateError


class AggregateProductUseCase:
    def __init__(self, product_repository: ProductRepository):
        self._product_repository = product_repository

    async def execute(self, product_id: UUID, aggregated_at: datetime | None = None) -> ProductEntity:
        """Агрегирует продукт"""
        product = await self._product_repository.get_or_raise(product_id)
        if product.is_aggregated:
            raise InvalidStateError("Продукт уже агрегирован")
        product.aggregate(aggregated_at)
        return await self._product_repository.update(product)
