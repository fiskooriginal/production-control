from typing import ClassVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.queries.ports import ProductQueryServiceProtocol
from src.application.queries.products import ListProductsQuery, ProductReadDTO, ProductSortField
from src.domain.shared.queries import QueryResult
from src.infrastructure.exceptions import DatabaseException
from src.infrastructure.persistence.mappers.query import product_model_to_read_dto
from src.infrastructure.persistence.models.product import Product


class ProductQueryService(ProductQueryServiceProtocol):
    SORT_FIELD_MAPPING: ClassVar = {
        ProductSortField.CREATED_AT: Product.created_at,
        ProductSortField.UPDATED_AT: Product.updated_at,
        ProductSortField.UNIQUE_CODE: Product.unique_code,
        ProductSortField.IS_AGGREGATED: Product.is_aggregated,
        ProductSortField.AGGREGATED_AT: Product.aggregated_at,
    }

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, product_id: UUID) -> ProductReadDTO | None:
        """Получает продукт по UUID"""
        try:
            product_model = await self._session.get(Product, product_id)
            if product_model is None:
                return None
            return product_model_to_read_dto(product_model)
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении продукта: {e}") from e

    async def list(self, query: ListProductsQuery) -> QueryResult[ProductReadDTO]:
        """Получает список продуктов с пагинацией и сортировкой"""
        try:
            stmt = select(Product)
            count_stmt = select(Product)

            if query.sort:
                stmt = self._apply_sort(stmt, query.sort)

            total_result = await self._session.execute(select(func.count()).select_from(count_stmt.subquery()))
            total = total_result.scalar_one() or 0

            if query.pagination:
                stmt = stmt.offset(query.pagination.offset).limit(query.pagination.limit)

            result = await self._session.execute(stmt)
            products = result.scalars().all()

            dtos = [product_model_to_read_dto(p) for p in products]

            return QueryResult(
                items=dtos,
                total=total,
                limit=query.pagination.limit if query.pagination else None,
                offset=query.pagination.offset if query.pagination else None,
            )
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении списка продуктов: {e}") from e

    def _apply_sort(self, stmt, sort):
        """Применяет сортировку к запросу"""
        from src.application.queries.products import ProductSortSpec

        if not isinstance(sort, ProductSortSpec):
            raise ValueError("sort должен быть типа ProductSortSpec")

        column = self.SORT_FIELD_MAPPING.get(sort.field)
        if column is None:
            raise ValueError(f"Неизвестное поле сортировки: {sort.field}")

        if sort.direction.value == "desc":
            column = column.desc()

        return stmt.order_by(column)
