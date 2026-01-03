import asyncio

import aio_pika

from aio_pika import RobustConnection
from aio_pika.abc import AbstractConnection

from src.core.logging import get_logger
from src.core.settings import RabbitMQSettings

logger = get_logger("rabbitmq.connection")


class RabbitMQConnection:
    """Управление подключением к RabbitMQ с автоматическим переподключением"""

    _connection: RobustConnection | None = None
    _lock: asyncio.Lock = asyncio.Lock()

    def __init__(self, settings: RabbitMQSettings) -> None:
        """
        Инициализирует менеджер подключения.

        Args:
            settings: Настройки подключения к RabbitMQ
        """
        self._settings = settings
        self._connection_url = self._build_connection_url()

    def _build_connection_url(self) -> str:
        """Строит URL для подключения к RabbitMQ"""
        return f"amqp://{self._settings.user}:{self._settings.password}@{self._settings.host}:{self._settings.port}/{self._settings.vhost}"

    async def get_connection(self) -> AbstractConnection:
        """
        Получает или создает подключение к RabbitMQ.

        Returns:
            Подключение к RabbitMQ

        Raises:
            Exception: При ошибке подключения
        """
        async with self._lock:
            if self._connection is None or self._connection.is_closed:
                logger.info(f"Connecting to RabbitMQ at {self._settings.host}:{self._settings.port}")
                self._connection = await aio_pika.connect_robust(
                    self._connection_url,
                    client_properties={"connection_name": "production-control"},
                )
                logger.info("Connected to RabbitMQ successfully")
            return self._connection

    async def close(self) -> None:
        """Закрывает подключение к RabbitMQ"""
        async with self._lock:
            if self._connection and not self._connection.is_closed:
                await self._connection.close()
                logger.info("RabbitMQ connection closed")
                self._connection = None
