from typing import Protocol

from src.domain.common.events import DomainEvent


class EventProducerProtocol(Protocol):
    """Протокол для публикации доменных событий в брокер сообщений"""

    async def publish(self, event: DomainEvent) -> None:
        """
        Публикует доменное событие в брокер сообщений.

        Args:
            event: Доменное событие для публикации

        Raises:
            Exception: При ошибке публикации события
        """
        ...
