from src.application.products.dtos import AggregateProductInputDTO
from src.application.uow import UnitOfWorkProtocol
from src.core.logging import get_logger
from src.domain.common.exceptions import InvalidStateError
from src.domain.products.entities import ProductEntity

logger = get_logger("use_case.products")


class AggregateProductUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, input_dto: AggregateProductInputDTO) -> ProductEntity:
        """Агрегирует продукт с автоматическим сохранением доменных событий в outbox"""
        logger.info(f"Aggregating product: product_id={input_dto.product_id}")
        try:
            async with self._uow:
                product = await self._uow.products.get_or_raise(input_dto.product_id)

                if product.is_aggregated:
                    raise InvalidStateError("Продукт уже агрегирован")

                product.aggregate(input_dto.aggregated_at)

                result = await self._uow.products.update(product)
                logger.info(f"Product aggregated successfully: product_id={input_dto.product_id}")
                return result
        except Exception as e:
            logger.exception(f"Failed to aggregate product: {e}")
            raise
