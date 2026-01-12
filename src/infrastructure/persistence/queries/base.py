from collections.abc import Callable
from typing import Any, ClassVar, TypeVar
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.common.queries import QueryResult
from src.infrastructure.common.exceptions import DatabaseException

DomainEntity = TypeVar("DomainEntity")
PersistenceModel = TypeVar("PersistenceModel")
ListQuery = TypeVar("ListQuery")
Filters = TypeVar("Filters")
SortField = TypeVar("SortField")


class BaseQueryService[DomainEntity, PersistenceModel, ListQuery, Filters, SortField]:
    """
    Базовый класс Query Service с общей логикой чтения.

    Типы:
    - DomainEntity: доменная сущность
    - PersistenceModel: модель БД
    - ListQuery: тип запроса списка (например, ListBatchesQuery)
    - Filters: тип фильтров (например, BatchReadFilters)
    - SortField: enum полей сортировки (например, BatchSortField)
    """

    SORT_FIELD_MAPPING: ClassVar[dict[Any, Any]] = {}

    def __init__(
        self,
        session: AsyncSession,
        model_class: type[PersistenceModel],
        to_domain_entity: Callable[[PersistenceModel], DomainEntity],
    ):
        self._session = session
        self._model_class = model_class
        self._to_domain_entity = to_domain_entity

    async def get(self, uuid: UUID) -> DomainEntity | None:
        """Получает доменную сущность по UUID"""
        try:
            stmt = select(self._model_class).where(self._model_class.uuid == uuid)
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                return None
            return self._to_domain_entity(model)
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении сущности: {e}") from e

    async def list(self, query: ListQuery) -> QueryResult[DomainEntity]:
        """Получает список сущностей с фильтрацией, пагинацией и сортировкой"""
        try:
            stmt = select(self._model_class)
            count_stmt = select(self._model_class)

            if hasattr(query, "filters") and query.filters:
                stmt, count_stmt = self._apply_filters(stmt, count_stmt, query.filters)

            if hasattr(query, "sort") and query.sort:
                stmt = self._apply_sort(stmt, query.sort)

            total_result = await self._session.execute(select(func.count()).select_from(count_stmt.subquery()))
            total = total_result.scalar_one() or 0

            if hasattr(query, "pagination") and query.pagination:
                stmt = stmt.offset(query.pagination.offset).limit(query.pagination.limit)

            result = await self._session.execute(stmt)
            models = result.scalars().all()

            entities = [self._to_domain_entity(model) for model in models]

            pagination = getattr(query, "pagination", None)
            return QueryResult[DomainEntity](
                items=entities,
                total=total,
                limit=pagination.limit if pagination else None,
                offset=pagination.offset if pagination else None,
            )
        except Exception as e:
            raise DatabaseException(f"Ошибка базы данных при получении списка сущностей: {e}") from e

    def _apply_filters(
        self,
        stmt: Select,
        count_stmt: Select,
        filters: Filters | None,
    ) -> tuple[Select, Select]:
        """
        Применяет фильтры к запросу.
        Должен быть переопределен в дочерних классах, если нужны фильтры.
        """
        return stmt, count_stmt

    def _apply_sort(self, stmt: Select, sort: Any) -> Select:
        """Применяет сортировку к запросу"""
        if not hasattr(sort, "field") or not hasattr(sort, "direction"):
            raise ValueError("sort должен иметь атрибуты field и direction")

        column = self.SORT_FIELD_MAPPING.get(sort.field)
        if column is None:
            raise ValueError(f"Неизвестное поле сортировки: {sort.field}")

        direction_value = sort.direction.value if hasattr(sort.direction, "value") else sort.direction
        if direction_value == "desc":
            column = column.desc()

        return stmt.order_by(column)
