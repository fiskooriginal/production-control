import asyncio

from dataclasses import dataclass

import httpx

from src.core.logging import get_logger
from src.core.time import datetime_now
from src.domain.webhooks.entities.delivery import WebhookDeliveryEntity
from src.domain.webhooks.entities.subscription import WebhookSubscriptionEntity
from src.domain.webhooks.enums import WebhookEventType
from src.infrastructure.webhooks.hmac import HMACSigner

logger = get_logger("webhooks.sender")


@dataclass(frozen=True)
class WebhookRequest:
    """Данные для отправки webhook запроса"""

    url: str
    payload: dict
    headers: dict[str, str]
    timeout: int


@dataclass(frozen=True)
class WebhookResponse:
    """Результат попытки отправки webhook"""

    success: bool
    status_code: int | None = None
    body: str | None = None
    error_message: str | None = None


class WebhookSender:
    """Сервис для отправки HTTP запросов webhooks с ретраями и таймаутом"""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Получает или создает HTTP клиент"""
        if self._client is None:
            self._client = httpx.AsyncClient()

        return self._client

    async def close(self) -> None:
        """Закрывает HTTP клиент"""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _build_webhook_payload(self, event_type: WebhookEventType, data: dict) -> dict:
        """Создает payload для webhook в формате {"event": "...", "timestamp": "...", "data": {...}}"""
        return {
            "event": event_type.value,
            "timestamp": datetime_now().isoformat(),
            "data": data,
        }

    def _build_request(
        self, subscription: WebhookSubscriptionEntity, event_type: WebhookEventType, payload: dict
    ) -> WebhookRequest:
        """Строит объект запроса с payload и заголовками"""
        webhook_payload = self._build_webhook_payload(event_type, payload)
        signature = HMACSigner.sign_payload(webhook_payload, subscription.secret_key.value)

        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event": event_type.value,
        }

        return WebhookRequest(
            url=subscription.url.value,
            payload=webhook_payload,
            headers=headers,
            timeout=subscription.timeout.value,
        )

    def _calculate_retry_delay(self, attempt_number: int) -> float:
        """Вычисляет задержку для ретрая с экспоненциальной задержкой"""
        base_delay = 1.0
        return base_delay * (2 ** (attempt_number - 1))

    async def _execute_request(self, request: WebhookRequest) -> WebhookResponse:
        """Выполняет одну попытку отправки HTTP запроса"""
        client = await self._get_client()

        try:
            response = await client.post(
                request.url,
                json=request.payload,
                headers=request.headers,
                timeout=request.timeout,
            )

            response_body = response.text[:1000] if response.text else ""

            if 200 <= response.status_code < 300:
                return WebhookResponse(
                    success=True,
                    status_code=response.status_code,
                    body=response_body,
                )

            return WebhookResponse(
                success=False,
                status_code=response.status_code,
                body=response_body,
                error_message=f"HTTP {response.status_code}: {response_body}",
            )

        except httpx.TimeoutException:
            return WebhookResponse(
                success=False,
                error_message=f"Timeout after {request.timeout}s",
            )

        except httpx.RequestError as e:
            return WebhookResponse(
                success=False,
                error_message=f"Request error: {e!s}",
            )

        except Exception as e:
            logger.exception(f"Неожиданная ошибка при отправке webhook: {e}")
            return WebhookResponse(
                success=False,
                error_message=f"Unexpected error: {e!s}",
            )

    async def send_webhook(
        self,
        subscription: WebhookSubscriptionEntity,
        event_type: WebhookEventType,
        payload: dict,
        delivery: WebhookDeliveryEntity,
    ) -> WebhookDeliveryEntity:
        """
        Отправляет webhook с ретраями и таймаутом.

        Args:
            subscription: Подписка на webhook
            event_type: Тип события
            payload: Данные события (извлеченные из доменного события)
            delivery: Сущность доставки для обновления

        Returns:
            Обновленная сущность доставки
        """
        request = self._build_request(subscription, event_type, payload)
        max_attempts = subscription.retry_count.value + 1

        for attempt in range(1, max_attempts + 1):
            delivery.increment_attempts()

            logger.info(
                f"Отправка webhook attempt={attempt}/{max_attempts} "
                f"subscription_id={subscription.id} event={event_type.value} url={request.url}"
            )

            response = await self._execute_request(request)

            if response.success:
                delivery.mark_success(
                    response_status=response.status_code or 200,
                    response_body=response.body or "",
                    delivered_at=datetime_now(),
                )

                logger.info(
                    f"Webhook успешно отправлен subscription_id={subscription.id} "
                    f"event={event_type.value} status={response.status_code} attempts={attempt}"
                )

                return delivery

            self._log_failed_attempt(subscription, event_type, attempt, response)

            if attempt < max_attempts:
                await self._wait_before_retry(attempt, subscription, event_type)

        final_error_message = f"Все попытки исчерпаны: {response.error_message or 'Unknown error'}"
        delivery.mark_failed(final_error_message)

        logger.error(
            f"Webhook не удалось отправить после {max_attempts} попыток "
            f"subscription_id={subscription.id} event={event_type.value}"
        )

        return delivery

    def _log_failed_attempt(
        self,
        subscription: WebhookSubscriptionEntity,
        event_type: WebhookEventType,
        attempt: int,
        response: WebhookResponse,
    ) -> None:
        """Логирует неудачную попытку отправки"""
        if response.status_code:
            logger.warning(
                f"Webhook вернул не успешный статус subscription_id={subscription.id} "
                f"event={event_type.value} status={response.status_code} attempt={attempt}"
            )
        else:
            logger.warning(
                f"Ошибка при отправке webhook subscription_id={subscription.id} "
                f"event={event_type.value} attempt={attempt} error={response.error_message}"
            )

    async def _wait_before_retry(
        self,
        attempt: int,
        subscription: WebhookSubscriptionEntity,
        event_type: WebhookEventType,
    ) -> None:
        """Ожидает перед повторной попыткой"""
        delay = self._calculate_retry_delay(attempt)
        logger.info(
            f"Повторная попытка через {delay}s subscription_id={subscription.id} "
            f"event={event_type.value} attempt={attempt + 1}"
        )
        await asyncio.sleep(delay)
