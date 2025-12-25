import builtins
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.products.entities import ProductEntity
from src.domain.products.repositories import ProductRepositoryProtocol
from src.domain.shared.exceptions import AlreadyExistsError, DoesNotExistError
from src.domain.shared.queries import PaginationSpec, QueryResult, SortSpec
from src.infrastructure.persistence.mappers.products import to_domain_entity, to_persistence_model
from src.infrastructure.persistence.models.product import Product


class ProductRepository(ProductRepositoryProtocol):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, domain_entity: ProductEntity) -> ProductEntity:
        """Создает новый продукт в репозитории"""
        existing = await self.get(domain_entity.uuid)
        if existing is not None:
            raise AlreadyExistsError(f"Продукт с UUID {domain_entity.uuid} уже существует")
        product_model = to_persistence_model(domain_entity)
        self._session.add(product_model)
        await self._session.flush()
        return to_domain_entity(product_model)

    async def get(self, uuid: UUID) -> ProductEntity | None:
        """Получает продукт по UUID"""
        product_model = await self._session.get(Product, uuid)
        if product_model is None:
            return None
        return to_domain_entity(product_model)

    async def get_or_raise(self, uuid: UUID) -> ProductEntity:
        """Получает продукт по UUID или выбрасывает исключение"""
        product = await self.get(uuid)
        if product is None:
            raise DoesNotExistError(f"Продукт с UUID {uuid} не найден")
        return product

    async def update(self, domain_entity: ProductEntity) -> ProductEntity:
        """Обновляет существующий продукт"""
        product_model = await self._session.get(Product, domain_entity.uuid)
        if product_model is None:
            raise DoesNotExistError(f"Продукт с UUID {domain_entity.uuid} не найден")
        updated_model = to_persistence_model(domain_entity)
        for key, value in updated_model.model_dump(exclude={"uuid", "created_at"}).items():
            setattr(product_model, key, value)
        await self._session.flush()
        return to_domain_entity(product_model)

    async def delete(self, uuid: UUID) -> None:
        """Удаляет продукт по UUID"""
        product_model = await self._session.get(Product, uuid)
        if product_model is None:
            raise DoesNotExistError(f"Продукт с UUID {uuid} не найден")
        await self._session.delete(product_model)

    async def exists(self, uuid: UUID) -> bool:
        """Проверяет существование продукта по UUID"""
        stmt = select(Product.uuid).where(Product.uuid == uuid)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def list(
        self,
        pagination: PaginationSpec | None = None,
        sort: SortSpec | None = None,
        filters: dict[str, Any] | None = None,
    ) -> QueryResult[ProductEntity]:
        """Получает список продуктов с пагинацией, сортировкой и фильтрацией"""
        stmt = select(Product)
        if filters:
            if "batch_id" in filters and filters["batch_id"] is not None:
                stmt = stmt.where(Product.batch_id == filters["batch_id"])
            if "is_aggregated" in filters and filters["is_aggregated"] is not None:
                stmt = stmt.where(Product.is_aggregated == filters["is_aggregated"])
        if sort:
            order_by = getattr(Product, sort.field)
            if sort.direction.value == "desc":
                order_by = order_by.desc()
            stmt = stmt.order_by(order_by)
        count_stmt = select(Product)
        if filters:
            if "batch_id" in filters and filters["batch_id"] is not None:
                count_stmt = count_stmt.where(Product.batch_id == filters["batch_id"])
            if "is_aggregated" in filters and filters["is_aggregated"] is not None:
                count_stmt = count_stmt.where(Product.is_aggregated == filters["is_aggregated"])
        total_result = await self._session.execute(select(func.count()).select_from(count_stmt.subquery()))
        total = total_result.scalar_one() or 0
        if pagination:
            stmt = stmt.offset(pagination.offset).limit(pagination.limit)
        result = await self._session.execute(stmt)
        products = result.scalars().all()
        entities = [to_domain_entity(p) for p in products]
        return QueryResult(
            items=entities,
            total=total,
            limit=pagination.limit if pagination else None,
            offset=pagination.offset if pagination else None,
        )

    async def get_by_unique_code(self, unique_code: str) -> ProductEntity | None:
        """Находит продукт по уникальному коду"""
        stmt = select(Product).where(Product.unique_code == unique_code)
        result = await self._session.execute(stmt)
        product_model = result.scalar_one_or_none()
        if product_model is None:
            return None
        return to_domain_entity(product_model)

    async def get_aggregated(self) -> builtins.list[ProductEntity]:
        """Находит все агрегированные продукты"""
        stmt = select(Product).where(Product.is_aggregated.is_(True))
        result = await self._session.execute(stmt)
        products = result.scalars().all()
        return [to_domain_entity(p) for p in products]

    async def get_by_ids(self, ids: builtins.list[UUID]) -> builtins.list[ProductEntity]:
        """Возвращает все продукты из переданного списка ID"""
        if not ids:
            return []
        stmt = select(Product).where(Product.uuid.in_(ids))
        result = await self._session.execute(stmt)
        products = result.scalars().all()
        return [to_domain_entity(p) for p in products]
