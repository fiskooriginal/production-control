from typing import Any, Protocol, TypeVar
from uuid import UUID

from src.domain.shared.queries import PaginationSpec, QueryResult, SortSpec

T = TypeVar("T")


class BaseRepositoryProtocol(Protocol[T]):
    async def create(self, entity: T) -> T:
        """Создает новую сущность в репозитории. Выбрасывает AlreadyExistsError, если сущность уже существует."""
        ...

    async def get(self, uuid: UUID) -> T | None:
        """Получает сущность по UUID. Возвращает None, если сущность не найдена."""
        ...

    async def get_or_raise(self, uuid: UUID) -> T:
        """Получает сущность по UUID. Выбрасывает DoesNotExistError, если сущность не найдена."""
        ...

    async def update(self, entity: T) -> T:
        """Обновляет существующую сущность. Выбрасывает DoesNotExistError, если сущность не найдена."""
        ...

    async def delete(self, uuid: UUID) -> None:
        """Удаляет сущность по UUID. Выбрасывает DoesNotExistError, если сущность не найдена."""
        ...

    async def exists(self, uuid: UUID) -> bool:
        """Проверяет существование сущности по UUID."""
        ...

    async def list(
        self,
        pagination: PaginationSpec | None = None,
        sort: SortSpec | None = None,
        filters: dict[str, Any] | None = None,
    ) -> QueryResult[T]:
        """Получает список сущностей с пагинацией, сортировкой и фильтрацией."""
        ...
