import json

from typing import TYPE_CHECKING

import aio_pika

if TYPE_CHECKING:
    from aio_pika.abc import AbstractChannel, AbstractExchange

from src.core.logging import get_logger
from src.core.settings import RabbitMQMessagingSettings
from src.domain.common.events import DomainEvent
from src.infrastructure.events.registry import EventRegistry
from src.infrastructure.events.serializer import EventSerializer
from src.infrastructure.messaging.rabbitmq.connection import RabbitMQConnection
from src.infrastructure.messaging.rabbitmq.mapper import EventRoutingMapper

logger = get_logger("rabbitmq.producer")


class RabbitMQEventProducer:
    """Реализация продюсера событий для RabbitMQ"""

    def __init__(
        self,
        connection: RabbitMQConnection,
        settings: RabbitMQMessagingSettings,
        routing_mapper: EventRoutingMapper,
    ) -> None:
        """
        Инициализирует продюсер.

        Args:
            connection: Менеджер подключения к RabbitMQ
            settings: Настройки messaging
            routing_mapper: Маппер для routing keys
        """
        self._connection = connection
        self._settings = settings
        self._routing_mapper = routing_mapper
        self._channel: AbstractChannel | None = None
        self._exchange: AbstractExchange | None = None

    async def _ensure_exchange(self) -> None:
        """Создает exchange если его еще нет"""
        if self._exchange is None:
            conn = await self._connection.get_connection()
            self._channel = await conn.channel()
            await self._channel.set_qos(prefetch_count=1)

            self._exchange = await self._channel.declare_exchange(
                self._settings.event_exchange,
                aio_pika.ExchangeType.TOPIC,
                durable=True,
            )
            logger.debug(f"Exchange '{self._settings.event_exchange}' declared")

    async def publish(self, event: DomainEvent) -> None:
        """
        Публикует доменное событие в RabbitMQ.

        Args:
            event: Доменное событие для публикации

        Raises:
            Exception: При ошибке публикации события
        """
        try:
            if not EventRegistry.is_registered(type(event)):
                logger.warning(f"Event {type(event).__name__} is not registered, skipping publication")
                return

            await self._ensure_exchange()

            event_name, _ = EventRegistry.get_event_metadata(type(event))
            routing_key = self._routing_mapper.get_routing_key(event_name)

            serialized_event = EventSerializer.serialize(event)
            message_body = json.dumps(serialized_event).encode("utf-8")

            message = aio_pika.Message(
                message_body,
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                headers={
                    "event_name": event_name,
                    "event_version": serialized_event["event_version"],
                    "aggregate_id": str(event.aggregate_id),
                },
            )

            await self._exchange.publish(message, routing_key=routing_key)
            logger.debug(f"Published event {event_name} (routing_key={routing_key}, aggregate_id={event.aggregate_id})")
        except Exception as e:
            logger.exception(f"Failed to publish event {type(event).__name__}: {e}")
            raise

    async def close(self) -> None:
        """Закрывает канал продюсера"""
        if self._channel and not self._channel.is_closed:
            await self._channel.close()
            self._channel = None
            self._exchange = None
