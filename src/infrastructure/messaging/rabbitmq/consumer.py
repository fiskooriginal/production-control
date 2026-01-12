from abc import abstractmethod
from typing import TYPE_CHECKING

import aio_pika

if TYPE_CHECKING:
    from aio_pika.abc import AbstractChannel, AbstractQueue

from src.core.logging import get_logger
from src.core.settings import RabbitMQMessagingSettings
from src.infrastructure.messaging.rabbitmq.connection import RabbitMQConnection
from src.infrastructure.messaging.rabbitmq.mapper import EventRoutingMapper

logger = get_logger("rabbitmq.consumer")


class RabbitMQEventConsumer:
    """Реализация консюмера событий для RabbitMQ"""

    def __init__(
        self,
        connection: RabbitMQConnection,
        settings: RabbitMQMessagingSettings,
        routing_mapper: EventRoutingMapper,
    ) -> None:
        """
        Инициализирует консюмер.

        Args:
            connection: Менеджер подключения к RabbitMQ
            settings: Настройки messaging
            routing_mapper: Маппер для routing keys
        """
        self._connection = connection
        self._settings = settings
        self._routing_mapper = routing_mapper
        self._channel: AbstractChannel | None = None
        self._queue: AbstractQueue | None = None
        self._is_running = False

    async def start(self) -> None:
        """
        Запускает консюмер для чтения событий.

        Raises:
            Exception: При ошибке запуска консюмера
        """
        if self._is_running:
            logger.warning("Consumer is already running")
            return

        try:
            conn = await self._connection.get_connection()
            self._channel = await conn.channel()
            await self._channel.set_qos(prefetch_count=self._settings.consumer_prefetch)

            exchange = await self._channel.declare_exchange(
                self._settings.event_exchange,
                aio_pika.ExchangeType.TOPIC,
                durable=True,
            )

            self._queue = await self._channel.declare_queue(
                self._settings.consumer_queue,
                durable=True,
            )

            await self._queue.bind(exchange, routing_key="#")

            logger.info(
                f"Consumer started: queue={self._settings.consumer_queue}, "
                f"exchange={self._settings.event_exchange}, prefetch={self._settings.consumer_prefetch}"
            )

            self._is_running = True

            async with self._queue.iterator() as queue_iter:
                async for message in queue_iter:
                    try:
                        await self.process_event(message)
                    except Exception as e:
                        logger.exception(f"Error handling message: {e}")
                        await message.nack(requeue=True)
        except Exception as e:
            logger.exception(f"Failed to start consumer: {e}")
            self._is_running = False
            raise

    async def stop(self) -> None:
        """
        Останавливает консюмер.

        Raises:
            Exception: При ошибке остановки консюмера
        """
        if not self._is_running:
            return

        self._is_running = False

        if self._channel and not self._channel.is_closed:
            await self._channel.close()
            self._channel = None
            self._queue = None

        logger.info("Consumer stopped")

    @abstractmethod
    async def process_message(self, message: aio_pika.IncomingMessage) -> None:
        """
        Обрабатывает входящее сообщение.

        Args:
            message: Входящее сообщение из RabbitMQ
        """
        raise NotImplementedError("Not implemented")
