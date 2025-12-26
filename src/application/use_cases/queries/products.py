from uuid import UUID

from src.application.queries.ports import ProductQueryServiceProtocol
from src.application.queries.products import ListProductsQuery, ProductReadDTO
from src.core.logging import get_logger
from src.domain.common.exceptions import DoesNotExistError
from src.domain.common.queries import QueryResult

logger = get_logger("use_case.queries.products")


class GetProductQueryUseCase:
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


class ListProductsQueryUseCase:
    def __init__(self, query_service: ProductQueryServiceProtocol):
        self._query_service = query_service

    async def execute(self, query: ListProductsQuery) -> QueryResult[ProductReadDTO]:
        """Получает список продуктов с пагинацией и сортировкой"""
        logger.debug(f"Listing products: pagination={query.pagination}, sort={query.sort}")
        try:
            result = await self._query_service.list(query)
            logger.debug(f"Listed {result.total} products")
            return result
        except Exception as e:
            logger.exception(f"Failed to list products: {e}")
            raise
