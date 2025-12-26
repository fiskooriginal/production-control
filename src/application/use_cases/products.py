from uuid import UUID

from src.application.dtos.products import AggregateProductInputDTO
from src.application.uow import UnitOfWorkProtocol
from src.core.logging import get_logger
from src.domain.products.entities import ProductEntity
from src.domain.shared.exceptions import InvalidStateError
from src.domain.shared.queries import PaginationSpec, QueryResult, SortSpec

logger = get_logger("use_case.products")


class AggregateProductUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, input_dto: AggregateProductInputDTO) -> ProductEntity:
        """Агрегирует продукт с автоматическим сохранением доменных событий в outbox"""
        logger.info(f"Aggregating product: product_id={input_dto.product_id}")
        try:
            async with self._uow:
                # Загружаем доменную сущность из репозитория
                product = await self._uow.products.get_or_raise(input_dto.product_id)

                # Валидация на уровне use case
                if product.is_aggregated:
                    raise InvalidStateError("Продукт уже агрегирован")

                # Работаем с доменной сущностью
                product.aggregate(input_dto.aggregated_at)

                # Сохраняем и возвращаем доменную сущность
                result = await self._uow.products.update(product)
                logger.info(f"Product aggregated successfully: product_id={input_dto.product_id}")
                return result
        except Exception as e:
            logger.exception(f"Failed to aggregate product: {e}")
            raise


class ListProductsUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(
        self,
        pagination: PaginationSpec | None = None,
        sort: SortSpec | None = None,
    ) -> QueryResult[ProductEntity]:
        """Получает список продуктов с пагинацией и сортировкой"""
        logger.debug(f"Listing products: pagination={pagination}, sort={sort}")
        try:
            async with self._uow:
                result = await self._uow.products.list(pagination=pagination, sort=sort)
                logger.debug(f"Listed {result.total} products")
                return result
        except Exception as e:
            logger.exception(f"Failed to list products: {e}")
            raise


class GetProductUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self._uow = uow

    async def execute(self, product_id: UUID) -> ProductEntity:
        """Получает продукт по UUID"""
        logger.debug(f"Getting product: product_id={product_id}")
        try:
            async with self._uow:
                result = await self._uow.products.get_or_raise(product_id)
                logger.debug(f"Product retrieved: product_id={product_id}")
                return result
        except Exception as e:
            logger.exception(f"Failed to get product: {e}")
            raise
