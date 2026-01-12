from uuid import UUID

from src.application.products.queries.dtos import ProductReadDTO
from src.application.products.queries.service import ProductQueryServiceProtocol
from src.core.logging import get_logger
from src.domain.common.exceptions import DoesNotExistError

logger = get_logger("query.handler.products")


class GetProductQueryHandler:
    def __init__(self, query_service: ProductQueryServiceProtocol):
        self._query_service = query_service

    async def execute(self, product_id: UUID) -> ProductReadDTO:
        """Получает продукт по UUID"""
        logger.debug(f"Getting product: product_id={product_id}")
        try:
            result = await self._query_service.get(product_id)
            if result is None:
                raise DoesNotExistError(f"Продукт с UUID {product_id} не найден")
            logger.debug(f"Product retrieved: product_id={product_id}")
            return result
        except DoesNotExistError:
            raise
        except Exception as e:
            logger.exception(f"Failed to get product: {e}")
            raise
