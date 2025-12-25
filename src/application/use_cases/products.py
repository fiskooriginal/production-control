from src.application.dtos.products import AggregateProductInputDTO
from src.application.uow import UnitOfWorkProtocol
from src.domain.products.entities import ProductEntity
from src.domain.shared.exceptions import InvalidStateError


class AggregateProductUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, input_dto: AggregateProductInputDTO) -> ProductEntity:
        """Агрегирует продукт с автоматическим сохранением доменных событий в outbox"""
        async with self._uow:
            # Загружаем доменную сущность из репозитория
            product = await self._uow.products.get_or_raise(input_dto.product_id)

            # Валидация на уровне use case
            if product.is_aggregated:
                raise InvalidStateError("Продукт уже агрегирован")

            # Работаем с доменной сущностью
            product.aggregate(input_dto.aggregated_at)

            # Сохраняем и возвращаем доменную сущность
            return await self._uow.products.update(product)
