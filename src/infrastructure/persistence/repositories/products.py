import builtins
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError, IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.products.entities import ProductEntity
from src.domain.products.repositories import ProductRepositoryProtocol
from src.domain.shared.exceptions import AlreadyExistsError, DoesNotExistError
from src.domain.shared.queries import PaginationSpec, QueryResult, SortSpec
from src.infrastructure.exceptions import DatabaseException, MappingException
from src.infrastructure.persistence.mappers.products import to_domain_entity, to_persistence_model
from src.infrastructure.persistence.models.product import Product


class ProductRepository(ProductRepositoryProtocol):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, domain_entity: ProductEntity) -> ProductEntity:
        """Создает новый продукт в репозитории"""
        try:
            existing = await self.get(domain_entity.uuid)
            if existing is not None:
                raise AlreadyExistsError(f"Продукт с UUID {domain_entity.uuid} уже существует")
            product_model = to_persistence_model(domain_entity)
            self._session.add(product_model)
            await self._session.flush()
            return to_domain_entity(product_model)
        except (AlreadyExistsError, DoesNotExistError):
            raise
        except IntegrityError as e:
            raise DatabaseException(f"Ошибка целостности данных при создании продукта: {e}") from e
        except DBAPIError as e:
            raise DatabaseException(f"Ошибка базы данных при создании продукта: {e}") from e
        except SQLAlchemyError as e:
            raise DatabaseException(f"Ошибка SQLAlchemy при создании продукта: {e}") from e
        except Exception as e:
            raise MappingException(f"Ошибка маппинга при создании продукта: {e}") from e

    async def get(self, uuid: UUID) -> ProductEntity | None:
        """Получает продукт по UUID"""
        try:
            product_model = await self._session.get(Product, uuid)
            if product_model is None:
                return None
            return to_domain_entity(product_model)
        except DBAPIError as e:
            raise DatabaseException(f"Ошибка базы данных при получении продукта: {e}") from e
        except SQLAlchemyError as e:
            raise DatabaseException(f"Ошибка SQLAlchemy при получении продукта: {e}") from e
        except Exception as e:
            raise MappingException(f"Ошибка маппинга при получении продукта: {e}") from e

    async def get_or_raise(self, uuid: UUID) -> ProductEntity:
        """Получает продукт по UUID или выбрасывает исключение"""
        product = await self.get(uuid)
        if product is None:
            raise DoesNotExistError(f"Продукт с UUID {uuid} не найден")
        return product

    async def update(self, domain_entity: ProductEntity) -> ProductEntity:
        """Обновляет существующий продукт"""
        try:
            product_model = await self._session.get(Product, domain_entity.uuid)
            if product_model is None:
                raise DoesNotExistError(f"Продукт с UUID {domain_entity.uuid} не найден")
            updated_model = to_persistence_model(domain_entity)
            for key, value in updated_model.model_dump(exclude={"uuid", "created_at"}).items():
                setattr(product_model, key, value)
            await self._session.flush()
            return to_domain_entity(product_model)
        except (AlreadyExistsError, DoesNotExistError):
            raise
        except IntegrityError as e:
            raise DatabaseException(f"Ошибка целостности данных при обновлении продукта: {e}") from e
        except DBAPIError as e:
            raise DatabaseException(f"Ошибка базы данных при обновлении продукта: {e}") from e
        except SQLAlchemyError as e:
            raise DatabaseException(f"Ошибка SQLAlchemy при обновлении продукта: {e}") from e
        except Exception as e:
            raise MappingException(f"Ошибка маппинга при обновлении продукта: {e}") from e

    async def delete(self, uuid: UUID) -> None:
        """Удаляет продукт по UUID"""
        try:
            product_model = await self._session.get(Product, uuid)
            if product_model is None:
                raise DoesNotExistError(f"Продукт с UUID {uuid} не найден")
            await self._session.delete(product_model)
        except (AlreadyExistsError, DoesNotExistError):
            raise
        except IntegrityError as e:
            raise DatabaseException(f"Ошибка целостности данных при удалении продукта: {e}") from e
        except DBAPIError as e:
            raise DatabaseException(f"Ошибка базы данных при удалении продукта: {e}") from e
        except SQLAlchemyError as e:
            raise DatabaseException(f"Ошибка SQLAlchemy при удалении продукта: {e}") from e

    async def exists(self, uuid: UUID) -> bool:
        """Проверяет существование продукта по UUID"""
        try:
            stmt = select(Product.uuid).where(Product.uuid == uuid)
            result = await self._session.execute(stmt)
            return result.scalar_one_or_none() is not None
        except DBAPIError as e:
            raise DatabaseException(f"Ошибка базы данных при проверке существования продукта: {e}") from e
        except SQLAlchemyError as e:
            raise DatabaseException(f"Ошибка SQLAlchemy при проверке существования продукта: {e}") from e

    async def list(
        self,
        pagination: PaginationSpec | None = None,
        sort: SortSpec | None = None,
        filters: dict[str, Any] | None = None,
    ) -> QueryResult[ProductEntity]:
        """Получает список продуктов с пагинацией, сортировкой и фильтрацией"""
        try:
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
        except DBAPIError as e:
            raise DatabaseException(f"Ошибка базы данных при получении списка продуктов: {e}") from e
        except SQLAlchemyError as e:
            raise DatabaseException(f"Ошибка SQLAlchemy при получении списка продуктов: {e}") from e
        except Exception as e:
            raise MappingException(f"Ошибка маппинга при получении списка продуктов: {e}") from e

    async def get_by_unique_code(self, unique_code: str) -> ProductEntity | None:
        """Находит продукт по уникальному коду"""
        try:
            stmt = select(Product).where(Product.unique_code == unique_code)
            result = await self._session.execute(stmt)
            product_model = result.scalar_one_or_none()
            if product_model is None:
                return None
            return to_domain_entity(product_model)
        except DBAPIError as e:
            raise DatabaseException(f"Ошибка базы данных при поиске продукта по коду: {e}") from e
        except SQLAlchemyError as e:
            raise DatabaseException(f"Ошибка SQLAlchemy при поиске продукта по коду: {e}") from e
        except Exception as e:
            raise MappingException(f"Ошибка маппинга при поиске продукта по коду: {e}") from e

    async def get_aggregated(self) -> builtins.list[ProductEntity]:
        """Находит все агрегированные продукты"""
        try:
            stmt = select(Product).where(Product.is_aggregated.is_(True))
            result = await self._session.execute(stmt)
            products = result.scalars().all()
            return [to_domain_entity(p) for p in products]
        except DBAPIError as e:
            raise DatabaseException(f"Ошибка базы данных при получении агрегированных продуктов: {e}") from e
        except SQLAlchemyError as e:
            raise DatabaseException(f"Ошибка SQLAlchemy при получении агрегированных продуктов: {e}") from e
        except Exception as e:
            raise MappingException(f"Ошибка маппинга при получении агрегированных продуктов: {e}") from e

    async def get_by_ids(self, ids: builtins.list[UUID]) -> builtins.list[ProductEntity]:
        """Возвращает все продукты из переданного списка ID"""
        try:
            if not ids:
                return []
            stmt = select(Product).where(Product.uuid.in_(ids))
            result = await self._session.execute(stmt)
            products = result.scalars().all()
            return [to_domain_entity(p) for p in products]
        except DBAPIError as e:
            raise DatabaseException(f"Ошибка базы данных при получении продуктов по ID: {e}") from e
        except SQLAlchemyError as e:
            raise DatabaseException(f"Ошибка SQLAlchemy при получении продуктов по ID: {e}") from e
        except Exception as e:
            raise MappingException(f"Ошибка маппинга при получении продуктов по ID: {e}") from e
