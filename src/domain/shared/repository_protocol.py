from typing import Protocol, TypeVar
from uuid import UUID

T = TypeVar("T")


class BaseRepositoryProtocol(Protocol[T]):
    async def get_or_raise(self, uuid: UUID) -> T:
        """Получает сущность по UUID для write-операций. Выбрасывает DoesNotExistError, если сущность не найдена."""
        ...

    async def create(self, domain_entity: T) -> T:
        """Создает новую доменную сущность в репозитории. Выбрасывает AlreadyExistsError, если сущность уже существует."""
        ...

    async def update(self, domain_entity: T) -> T:
        """Обновляет существующую доменную сущность. Выбрасывает DoesNotExistError, если сущность не найдена."""
        ...

    async def delete(self, uuid: UUID) -> None:
        """Удаляет сущность по UUID. Выбрасывает DoesNotExistError, если сущность не найдена."""
        ...
