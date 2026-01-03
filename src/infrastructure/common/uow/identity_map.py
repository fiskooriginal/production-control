from typing import TypeVar
from uuid import UUID

from src.domain.common.entities import BaseEntity

T = TypeVar("T", bound=BaseEntity)


class IdentityMap:
    """
    Identity Map для отслеживания загруженных/измененных агрегатов в рамках UOW.
    Хранит агрегаты по UUID для извлечения доменных событий.
    """

    def __init__(self) -> None:
        self._entities: dict[UUID, BaseEntity] = {}

    def add(self, entity: BaseEntity) -> None:
        """
        Добавляет сущность в identity map.
        Если сущность уже есть, объединяет события из новой версии с существующими.
        """
        if entity.uuid not in self._entities:
            self._entities[entity.uuid] = entity
        else:
            # Сущность уже есть - объединяем события из новой версии
            existing_entity = self._entities[entity.uuid]

            # Создаем копию списка событий, чтобы избежать бесконечного цикла
            # если entity и existing_entity - это один и тот же объект
            new_events = list(entity.get_domain_events())
            existing_events = existing_entity.get_domain_events()

            # Добавляем только те события, которых еще нет в existing_entity
            # чтобы избежать дублирования при сохранении в outbox
            for event in new_events:
                if event not in existing_events:
                    existing_entity.add_domain_event(event)

    def get(self, entity_id: UUID) -> BaseEntity | None:
        """Получает сущность из identity map"""
        return self._entities.get(entity_id)

    def contains(self, entity_id: UUID) -> bool:
        """Проверяет, содержится ли сущность в identity map"""
        return entity_id in self._entities

    def get_all(self) -> list[BaseEntity]:
        """Возвращает все отслеживаемые сущности"""
        return list(self._entities.values())

    def clear(self) -> None:
        """Очищает identity map"""
        self._entities.clear()
