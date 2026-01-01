from typing import ClassVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.products.queries import ListProductsQuery, ProductQueryServiceProtocol
from src.application.products.queries.sort import ProductSortField
from src.domain.common.queries import QueryResult
from src.domain.products import ProductEntity
from src.infrastructure.common.exceptions import DatabaseException
from src.infrastructure.persistence.mappers.products import to_domain_entity
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

    async def get(self, product_id: UUID) -> ProductEntity | None:
        """Получает продукт по UUID"""
        try:
            stmt = select(Product).where(Product.uuid == product_id)
            result = await self._session.execute(stmt)
            product_model = result.scalar_one_or_none()
            if product_model is None:
                return None
            return to_domain_entity(product_model)
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении продукта: {e}") from e

    async def list(self, query: ListProductsQuery) -> QueryResult[ProductEntity]:
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

            entities = [to_domain_entity(p) for p in products]

            return QueryResult[ProductEntity](
                items=entities,
                total=total,
                limit=query.pagination.limit if query.pagination else None,
                offset=query.pagination.offset if query.pagination else None,
            )
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении списка продуктов: {e}") from e

    def _apply_sort(self, stmt, sort):
        """Применяет сортировку к запросу"""
        from src.application.products.queries import ProductSortSpec

        if not isinstance(sort, ProductSortSpec):
            raise ValueError("sort должен быть типа ProductSortSpec")

        column = self.SORT_FIELD_MAPPING.get(sort.field)
        if column is None:
            raise ValueError(f"Неизвестное поле сортировки: {sort.field}")

        if sort.direction.value == "desc":
            column = column.desc()

        return stmt.order_by(column)
