from datetime import datetime
from uuid import UUID

from src.application.uow import UnitOfWorkProtocol
from src.domain.products.entities import ProductEntity
from src.domain.shared.exceptions import InvalidStateError


class AggregateProductUseCase:
    """
    Use case для агрегации продукта.
    Использует UnitOfWork для атомарного обновления продукта и сохранения доменных событий.
    """

    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, product_id: UUID, aggregated_at: datetime | None = None) -> ProductEntity:
        """Агрегирует продукт с автоматическим сохранением доменных событий в outbox"""
        async with self._uow:
            product = await self._uow.products.get_or_raise(product_id)
            if product.is_aggregated:
                raise InvalidStateError("Продукт уже агрегирован")
            product.aggregate(aggregated_at)
            result = await self._uow.products.update(product)
            return result
