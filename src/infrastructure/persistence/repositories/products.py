from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.products import ProductEntity
from src.domain.products.interfaces.repository import ProductRepositoryProtocol
from src.infrastructure.common.exceptions import DatabaseException
from src.infrastructure.persistence.mappers.products import to_domain_entity, to_persistence_model
from src.infrastructure.persistence.models.product import Product
from src.infrastructure.persistence.repositories.base import BaseRepository


class ProductRepository(BaseRepository[ProductEntity, Product], ProductRepositoryProtocol):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Product, to_domain_entity, to_persistence_model)

    async def get_by_unique_code(self, unique_code: str, batch_id: UUID) -> ProductEntity | None:
        """Находит продукт по уникальному коду и идентификатору партии"""
        try:
            stmt = select(self._model_class).where(
                self._model_class.unique_code == unique_code, self._model_class.batch_id == batch_id
            )
            result = await self._session.execute(stmt)
            product_model = result.scalar_one_or_none()
            if product_model is None:
                return None
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при поиске продукта по коду: {e}") from e

        return self._to_domain_entity(product_model)

    async def get_aggregated(self) -> list[ProductEntity]:
        """Находит все агрегированные продукты"""
        try:
            stmt = select(self._model_class).where(self._model_class.is_aggregated.is_(True))
            result = await self._session.execute(stmt)
            products = result.scalars().all()
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении агрегированных продуктов: {e}") from e

        return [self._to_domain_entity(p) for p in products]

    async def get_by_ids(self, ids: list[UUID]) -> list[ProductEntity]:
        """Возвращает все продукты из переданного списка ID"""
        try:
            if not ids:
                return []
            stmt = select(self._model_class).where(self._model_class.uuid.in_(ids))
            result = await self._session.execute(stmt)
            products = result.scalars().all()
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении продуктов по ID: {e}") from e

        return [self._to_domain_entity(p) for p in products]

    async def get_by_unique_codes(self, unique_codes: list[str]) -> list[ProductEntity]:
        """Возвращает все продукты из переданного списка уникальных кодов"""
        try:
            if not unique_codes:
                return []
            stmt = select(self._model_class).where(self._model_class.unique_code.in_(unique_codes))
            result = await self._session.execute(stmt)
            products = result.scalars().all()
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении продуктов по уникальным кодам: {e}") from e

        return [self._to_domain_entity(p) for p in products]
