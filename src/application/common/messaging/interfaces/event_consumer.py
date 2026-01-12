from typing import Any, Protocol


class EventConsumerProtocol(Protocol):
    """Протокол для чтения доменных событий из брокера сообщений"""

    async def start(self) -> None:
        """
        Запускает консюмер для чтения событий.

        Raises:
            Exception: При ошибке запуска консюмера
        """
        ...

    async def stop(self) -> None:
        """
        Останавливает консюмер.

        Raises:
            Exception: При ошибке остановки консюмера
        """
        ...

    async def process_message(self, message: Any) -> None:
        """
        Обрабатывает входящее сообщение.

        Args:
            message: Входящее сообщение из брокера сообщений

        Raises:
            Exception: При ошибке обработки сообщения
        """
        ...
