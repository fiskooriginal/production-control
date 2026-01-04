import asyncio
import json

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import UUID

import aio_pika

from sqlalchemy.exc import DBAPIError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logging import get_logger
from src.core.settings import CelerySettings, RabbitMQMessagingSettings
from src.domain.common.enums import EventTypesEnum
from src.domain.common.events import DomainEvent
from src.domain.webhooks.entities.delivery import WebhookDeliveryEntity
from src.domain.webhooks.entities.subscription import WebhookSubscriptionEntity
from src.domain.webhooks.enums import WebhookStatus
from src.domain.webhooks.value_objects import WebhookPayload
from src.infrastructure.background_tasks.app import (
    celery_app,
    get_event_consumer,
    get_rabbitmq_connection,
    get_session_factory,
    run_async_task,
)
from src.infrastructure.events.registry import EventRegistry
from src.infrastructure.events.serializer import EventSerializer
from src.infrastructure.persistence.queries.webhooks.subscription import WebhookSubscriptionQueryService
from src.infrastructure.persistence.repositories.event_type import EventTypeRepository
from src.infrastructure.persistence.repositories.webhooks.delivery import WebhookDeliveryRepository
from src.infrastructure.webhooks.sender import WebhookSender

if TYPE_CHECKING:
    from aio_pika.abc import AbstractQueue

logger = get_logger("celery.tasks.process_webhook_events")

celery_settings = CelerySettings()
messaging_settings = RabbitMQMessagingSettings()


@dataclass
class ProcessingStats:
    """Статистика обработки webhook событий"""

    processed: int = 0
    webhooks_sent: int = 0
    webhooks_failed: int = 0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Преобразует статистику в словарь"""
        return {
            "success": True,
            "processed": self.processed,
            "webhooks_sent": self.webhooks_sent,
            "webhooks_failed": self.webhooks_failed,
            "errors": self.errors,
        }


def _is_retryable_error(exception: Exception) -> bool:
    """Проверяет, является ли ошибка повторяемой (retryable)"""
    return isinstance(exception, (OperationalError, DBAPIError))


async def _get_active_subscriptions_for_event(
    query_service: WebhookSubscriptionQueryService, event_type: EventTypesEnum
) -> list[WebhookSubscriptionEntity]:
    """
    Получает активные подписки для указанного типа события.

    Args:
        query_service: Сервис для запросов подписок
        event_type: Тип события webhook

    Returns:
        Список активных подписок, которые подписаны на указанный тип события
    """
    from src.application.webhooks.queries.filters import WebhookReadFilters
    from src.application.webhooks.queries.queries import ListWebhookSubscriptionsQuery
    from src.domain.common.queries import PaginationSpec

    query = ListWebhookSubscriptionsQuery(
        filters=WebhookReadFilters(event_type=event_type),
        pagination=PaginationSpec(limit=1000, offset=0),
    )
    result = await query_service.list(query)

    active_subscriptions = [sub for sub in result.items if sub.is_active]
    logger.debug(f"Found {len(active_subscriptions)} active subscriptions for event_type={event_type!s}")
    return active_subscriptions


def _extract_event_payload(event: DomainEvent) -> dict:
    """
    Извлекает payload из доменного события.

    Args:
        event: Доменное событие

    Returns:
        Словарь с данными события (сериализованные значения)
    """
    payload = {}
    for field_name, field_value in event.__dict__.items():
        if field_name in ("occurred_at", "aggregate_id"):
            continue
        payload[field_name] = EventSerializer._serialize_value(field_value)

    payload["aggregate_id"] = str(event.aggregate_id)
    payload["occurred_at"] = event.occurred_at.isoformat()

    return payload


def _create_delivery_entity(
    subscription: WebhookSubscriptionEntity, event_type_id: UUID, event_type: EventTypesEnum, payload: dict
) -> WebhookDeliveryEntity:
    """
    Создает сущность доставки webhook со статусом PENDING.

    Args:
        subscription: Подписка на webhook
        event_type_id: UUID типа события
        event_type: Тип события
        payload: Данные события

    Returns:
        Сущность доставки со статусом PENDING
    """
    return WebhookDeliveryEntity(
        subscription_id=subscription.uuid,
        event_type_id=event_type_id,
        event_type=event_type,
        payload=WebhookPayload(payload),
        status=WebhookStatus.PENDING,
    )


async def _read_rabbitmq_messages(
    limit: int, timeout: float = 1.0
) -> tuple[list[aio_pika.IncomingMessage], aio_pika.abc.AbstractChannel]:
    """
    Читает сообщения из очереди RabbitMQ с таймаутом.

    Args:
        limit: Максимальное количество сообщений для чтения
        timeout: Таймаут в секундах для чтения одного сообщения

    Returns:
        Кортеж из списка прочитанных сообщений и канала (канал нужно закрыть после обработки сообщений)
    """
    messages = []
    rabbitmq_connection = get_rabbitmq_connection()
    conn = await rabbitmq_connection.get_connection()
    channel = await conn.channel()
    await channel.set_qos(prefetch_count=messaging_settings.consumer_prefetch)

    exchange = await channel.declare_exchange(
        messaging_settings.event_exchange,
        aio_pika.ExchangeType.TOPIC,
        durable=True,
    )

    queue: AbstractQueue = await channel.declare_queue(
        messaging_settings.consumer_queue,
        durable=True,
    )

    await queue.bind(exchange, routing_key="#")

    logger.debug(f"Reading messages from queue: {messaging_settings.consumer_queue}, limit={limit}")

    for _ in range(limit):
        try:
            message = await asyncio.wait_for(queue.get(timeout=timeout), timeout=timeout)
            if message is None:
                break
            messages.append(message)
            logger.debug(f"Read message from queue: delivery_tag={message.delivery_tag}")
        except TimeoutError:
            logger.debug("Timeout while reading message from queue")
            break
        except Exception as e:
            logger.warning(f"Error reading message from queue: {e}")
            break

    logger.info(f"Read {len(messages)} messages from queue")
    return messages, channel


async def _deserialize_rabbitmq_message(message: aio_pika.IncomingMessage) -> DomainEvent | None:
    """
    Десериализует сообщение из RabbitMQ в доменное событие.

    Args:
        message: Сообщение из RabbitMQ

    Returns:
        Десериализованное доменное событие или None в случае ошибки

    Note:
        Сообщение НЕ ACK/NACK здесь - это должно быть сделано в вызывающем коде
    """
    try:
        body = message.body
        data = json.loads(body.decode("utf-8"))
        event = EventSerializer.deserialize(data)
        logger.debug(f"Deserialized event: {type(event).__name__}, aggregate_id={event.aggregate_id}")
        return event
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from message body: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to deserialize message: {e}", exc_info=True)
        return None


@celery_app.task(bind=True, max_retries=None, name="tasks.process_webhook_events")
def process_webhook_events(self) -> dict:
    """
    Обрабатывает события из RabbitMQ и отправляет webhooks.

    Читает сообщения из очереди RabbitMQ, десериализует события,
    находит активные подписки и отправляет webhooks.

    Returns:
        {
            "success": True,
            "processed": 0,
            "webhooks_sent": 0,
            "webhooks_failed": 0,
            "errors": []
        }
    """
    return run_async_task(_process_webhook_events_async(self))


async def _process_single_subscription(
    subscription: WebhookSubscriptionEntity,
    event_type_id: UUID,
    event_type: EventTypesEnum,
    event_payload: dict,
    delivery_repository: WebhookDeliveryRepository,
    webhook_sender: WebhookSender,
    stats: ProcessingStats,
) -> None:
    """
    Обрабатывает одну подписку: создает delivery, отправляет webhook и обновляет статус.

    Args:
        subscription: Подписка на webhook
        event_type_id: UUID типа события
        event_type: Тип события
        event_payload: Данные события
        delivery_repository: Репозиторий для доставок
        webhook_sender: Сервис для отправки webhooks
        stats: Статистика обработки
    """
    try:
        delivery = _create_delivery_entity(subscription, event_type_id, event_type, event_payload)
        delivery = await delivery_repository.create(delivery)

        logger.debug(
            f"Created delivery subscription_id={subscription.uuid} "
            f"event_type={event_type!s} delivery_id={delivery.uuid}"
        )

        delivery = await webhook_sender.send_webhook(
            subscription=subscription,
            event_type=event_type,
            payload=event_payload,
            delivery=delivery,
        )

        await delivery_repository.update(delivery)

        if delivery.status == WebhookStatus.SUCCESS:
            stats.webhooks_sent += 1
            logger.info(
                f"Webhook sent successfully subscription_id={subscription.uuid} "
                f"event_type={event_type!s} delivery_id={delivery.uuid}"
            )
        else:
            stats.webhooks_failed += 1
            logger.warning(
                f"Webhook failed subscription_id={subscription.uuid} "
                f"event_type={event_type!s} delivery_id={delivery.uuid} "
                f"error={delivery.error_message}"
            )

    except Exception as e:
        stats.webhooks_failed += 1
        logger.error(
            f"Error processing webhook subscription_id={subscription.uuid} event_type={event_type!s}: {e}",
            exc_info=True,
        )
        stats.errors.append(f"Subscription {subscription.uuid!s}: {e!s}")


async def _process_single_event(
    event: DomainEvent,
    message: aio_pika.IncomingMessage,
    query_service: WebhookSubscriptionQueryService,
    delivery_repository: WebhookDeliveryRepository,
    webhook_sender: WebhookSender,
    session: AsyncSession,
    stats: ProcessingStats,
) -> None:
    """
    Обрабатывает одно событие: находит подписки и отправляет webhooks.

    Args:
        event: Доменное событие
        message: Сообщение из RabbitMQ
        query_service: Сервис для запросов подписок
        delivery_repository: Репозиторий для доставок
        webhook_sender: Сервис для отправки webhooks
        session: Сессия базы данных
        stats: Статистика обработки
    """
    try:
        stats.processed += 1
        logger.debug(f"Processing event: {type(event).__name__}, aggregate_id={event.aggregate_id}")

        event_name, _ = EventRegistry.get_event_metadata(type(event))

        try:
            webhook_event_type = EventTypesEnum(event_name)
        except ValueError:
            logger.debug(f"Event {event_name} not supported by webhooks, skipping: aggregate_id={event.aggregate_id}")
            await message.ack()
            return

        active_subscriptions = await _get_active_subscriptions_for_event(query_service, webhook_event_type)

        if not active_subscriptions:
            logger.debug(
                f"No active subscriptions for event_type={webhook_event_type!s}, aggregate_id={event.aggregate_id}"
            )
            await message.ack()
            return

        event_payload = _extract_event_payload(event)

        event_type_repository = EventTypeRepository(session)
        event_type_model = await event_type_repository.get_by_event_type(webhook_event_type)
        if event_type_model is None:
            logger.error(
                f"Event type {webhook_event_type} not found in database, skipping webhook delivery: "
                f"aggregate_id={event.aggregate_id}"
            )
            await message.ack()
            return

        for subscription in active_subscriptions:
            await _process_single_subscription(
                subscription=subscription,
                event_type_id=event_type_model.uuid,
                event_type=webhook_event_type,
                event_payload=event_payload,
                delivery_repository=delivery_repository,
                webhook_sender=webhook_sender,
                stats=stats,
            )

        await session.commit()
        await message.ack()
        logger.debug(f"Acknowledged message: delivery_tag={message.delivery_tag}")

    except Exception as e:
        logger.error(f"Error processing event: {e}", exc_info=True)
        stats.errors.append(str(e))
        await session.rollback()
        try:
            await message.nack(requeue=True)
            logger.debug(f"Nacked message with requeue: delivery_tag={message.delivery_tag}")
        except Exception as nack_error:
            logger.error(f"Failed to nack message: {nack_error}")


async def _process_webhook_events_async(task_instance) -> dict:
    """Асинхронная часть задачи обработки webhook событий"""
    session_factory = get_session_factory()
    stats = ProcessingStats()
    channel = None

    try:
        async with session_factory() as session:
            logger.info("Starting webhook events processing")

            get_event_consumer()
            messages, channel = await _read_rabbitmq_messages(limit=100, timeout=1.0)

            query_service = WebhookSubscriptionQueryService(session)
            delivery_repository = WebhookDeliveryRepository(session)
            webhook_sender = WebhookSender()

            try:
                for message in messages:
                    event = await _deserialize_rabbitmq_message(message)
                    if event is None:
                        logger.warning(f"Failed to deserialize message, nacking: delivery_tag={message.delivery_tag}")
                        await message.nack(requeue=False)
                        continue

                    await _process_single_event(
                        event=event,
                        message=message,
                        query_service=query_service,
                        delivery_repository=delivery_repository,
                        webhook_sender=webhook_sender,
                        session=session,
                        stats=stats,
                    )

            finally:
                await webhook_sender.close()
                if channel and not channel.is_closed:
                    await channel.close()
                    logger.debug("Closed RabbitMQ channel")

            logger.info(
                f"Webhook events processing completed: processed={stats.processed}, "
                f"webhooks_sent={stats.webhooks_sent}, webhooks_failed={stats.webhooks_failed}"
            )

            return stats.to_dict()

    except Exception as e:
        logger.exception(f"Failed to process webhook events: {e}")
        if channel and not channel.is_closed:
            try:
                await channel.close()
            except Exception as close_error:
                logger.warning(f"Error closing channel: {close_error}")
        if _is_retryable_error(e) and task_instance.request.retries < celery_settings.task_max_retries:
            raise task_instance.retry(
                exc=e,
                countdown=celery_settings.task_default_retry_delay,
            ) from e
        raise
