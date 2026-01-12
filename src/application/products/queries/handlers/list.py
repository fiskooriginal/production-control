from src.application.products.queries.queries import ListProductsQuery
from src.application.products.queries.service import ProductQueryServiceProtocol
from src.core.logging import get_logger
from src.domain.common.queries import QueryResult
from src.domain.products import ProductEntity

logger = get_logger("query.handler.products")


class ListProductsQueryHandler:
    def __init__(self, query_service: ProductQueryServiceProtocol):
        self._query_service = query_service

    async def execute(self, query: ListProductsQuery) -> QueryResult[ProductEntity]:
        """Получает список продуктов с пагинацией и сортировкой"""
        logger.debug(f"Listing products: pagination={query.pagination}, sort={query.sort}")
        try:
            result = await self._query_service.list(query)
            logger.debug(f"Listed {result.total} products")
            return result
        except Exception as e:
            logger.exception(f"Failed to list products: {e}")
            raise
