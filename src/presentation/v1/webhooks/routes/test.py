from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Query, Request, status

from src.core.logging import get_logger
from src.infrastructure.webhooks.hmac import HMACSigner
from src.presentation.v1.webhooks.schemas import WebhookTestResponse

logger = get_logger("webhooks.test")

router = APIRouter()


@router.post("/test", response_model=WebhookTestResponse, status_code=status.HTTP_200_OK)
async def test_webhook(
    request: Request,
    secret_key: Annotated[str | None, Query(description="Секретный ключ для проверки подписи")] = None,
) -> WebhookTestResponse:
    """
    Тестовый эндпоинт для приема и логирования webhook запросов.
    Принимает произвольный JSON body и логирует все данные.
    """
    received_at = datetime.now(UTC).isoformat()

    headers_dict = dict(request.headers)
    signature_header = headers_dict.get("X-Webhook-Signature")
    event_header = headers_dict.get("X-Webhook-Event")

    try:
        payload = await request.json()
    except Exception as e:
        logger.warning(f"Ошибка при парсинге JSON body: {e}")
        payload = {}

    signature_valid: bool | None = None

    if secret_key and signature_header:
        try:
            signature_valid = HMACSigner.verify_signature(payload, signature_header, secret_key)
            logger.info(f"Проверка подписи: valid={signature_valid}")
        except Exception as e:
            logger.warning(f"Ошибка при проверке подписи: {e}")
            signature_valid = False
    elif secret_key and not signature_header:
        logger.warning("Передан secret_key, но заголовок X-Webhook-Signature отсутствует")
        signature_valid = False

    logger.info(
        f"Получен webhook запрос: event={event_header}, "
        f"signature_valid={signature_valid}, received_at={received_at}, "
        f"headers={headers_dict}, payload={payload}"
    )

    return WebhookTestResponse(
        status="received",
        received_at=received_at,
        event=event_header,
        signature_valid=signature_valid,
        headers=headers_dict,
        payload=payload,
    )
