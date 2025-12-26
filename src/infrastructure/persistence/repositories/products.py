import builtins
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.products.entities import ProductEntity
from src.domain.products.repositories import ProductRepositoryProtocol
from src.domain.shared.exceptions import AlreadyExistsError, DoesNotExistError
from src.infrastructure.exceptions import DatabaseException
from src.infrastructure.persistence.mappers.products import to_domain_entity, to_persistence_model
from src.infrastructure.persistence.models.product import Product


class ProductRepository(ProductRepositoryProtocol):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_or_raise(self, uuid: UUID) -> ProductEntity:
        """Получает продукт по UUID для write-операций"""
        try:
            product_model = await self._session.get(Product, uuid)
            if product_model is None:
                raise DoesNotExistError(f"Продукт с UUID {uuid} не найден")
            return to_domain_entity(product_model)
        except DoesNotExistError:
            raise
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении продукта: {e}") from e

    async def create(self, domain_entity: ProductEntity) -> ProductEntity:
        """Создает новый продукт в репозитории"""
        try:
            stmt = select(Product.uuid).where(Product.uuid == domain_entity.uuid)
            result = await self._session.execute(stmt)
            if result.scalar_one_or_none() is not None:
                raise AlreadyExistsError(f"Продукт с UUID {domain_entity.uuid} уже существует")
        except AlreadyExistsError:
            raise
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при проверке существования продукта: {e}") from e

        product_model = to_persistence_model(domain_entity)

        try:
            self._session.add(product_model)
            await self._session.flush()
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при создании продукта: {e}") from e

        return to_domain_entity(product_model)

    async def update(self, domain_entity: ProductEntity) -> ProductEntity:
        """Обновляет существующий продукт"""
        product_model = await self._session.get(Product, domain_entity.uuid)
        if product_model is None:
            raise DoesNotExistError(f"Продукт с UUID {domain_entity.uuid} не найден")

        updated_model = to_persistence_model(domain_entity)
        for key, value in updated_model.model_dump(exclude={"uuid", "created_at"}).items():
            setattr(product_model, key, value)

        try:
            await self._session.flush()
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при обновлении продукта: {e}") from e

        return to_domain_entity(product_model)

    async def delete(self, uuid: UUID) -> None:
        """Удаляет продукт по UUID"""
        try:
            product_model = await self._session.get(Product, uuid)
            if product_model is None:
                raise DoesNotExistError(f"Продукт с UUID {uuid} не найден")
            await self._session.delete(product_model)
        except DoesNotExistError:
            raise
        except Exception as e:
            raise DatabaseException(f"Ошибка при удалении продукта: {e}") from e

    async def get_by_unique_code(self, unique_code: str) -> ProductEntity | None:
        """Находит продукт по уникальному коду"""
        try:
            stmt = select(Product).where(Product.unique_code == unique_code)
            result = await self._session.execute(stmt)
            product_model = result.scalar_one_or_none()
            if product_model is None:
                return None
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при поиске продукта по коду: {e}") from e

        return to_domain_entity(product_model)

    async def get_aggregated(self) -> builtins.list[ProductEntity]:
        """Находит все агрегированные продукты"""
        try:
            stmt = select(Product).where(Product.is_aggregated.is_(True))
            result = await self._session.execute(stmt)
            products = result.scalars().all()
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении агрегированных продуктов: {e}") from e

        return [to_domain_entity(p) for p in products]

    async def get_by_ids(self, ids: builtins.list[UUID]) -> builtins.list[ProductEntity]:
        """Возвращает все продукты из переданного списка ID"""
        try:
            if not ids:
                return []
            stmt = select(Product).where(Product.uuid.in_(ids))
            result = await self._session.execute(stmt)
            products = result.scalars().all()
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении продуктов по ID: {e}") from e

        return [to_domain_entity(p) for p in products]
