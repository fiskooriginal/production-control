import hashlib
import hmac
import json

from src.core.logging import get_logger

logger = get_logger("webhooks.hmac")


class HMACSigner:
    """Сервис для создания и проверки HMAC подписей webhook payload"""

    @staticmethod
    def sign_payload(payload: dict, secret_key: str) -> str:
        """
        Создает HMAC-SHA256 подпись для webhook payload.

        Args:
            payload: Словарь с данными для подписи
            secret_key: Секретный ключ для подписи

        Returns:
            Подпись в формате 'sha256=hex_signature'

        Raises:
            ValueError: Если secret_key пустой или payload невалидный
        """
        try:
            if not secret_key:
                raise ValueError("secret_key не может быть пустым")

            payload_json = json.dumps(payload, sort_keys=True, ensure_ascii=False)
            payload_bytes = payload_json.encode("utf-8")
            secret_bytes = secret_key.encode("utf-8")

            signature = hmac.new(secret_bytes, payload_bytes, hashlib.sha256).hexdigest()

            return f"sha256={signature}"
        except (TypeError, ValueError) as e:
            logger.warning(f"Ошибка при создании подписи: {e}")
            raise ValueError(f"Не удалось создать подпись: {e}") from e
        except Exception as e:
            logger.warning(f"Неожиданная ошибка при создании подписи: {e}")
            raise ValueError(f"Не удалось создать подпись: {e}") from e

    @staticmethod
    def verify_signature(payload: dict, signature: str, secret_key: str) -> bool:
        """
        Проверяет HMAC-SHA256 подпись для webhook payload.

        Args:
            payload: Словарь с данными для проверки
            signature: Подпись в формате 'sha256=hex_signature'
            secret_key: Секретный ключ для проверки

        Returns:
            True если подпись валидна, False в противном случае
        """
        try:
            if not secret_key:
                logger.warning("secret_key пустой при проверке подписи")
                return False

            if not signature:
                logger.warning("signature пустая при проверке подписи")
                return False

            if not signature.startswith("sha256="):
                logger.warning(f"Неверный формат подписи: {signature}")
                return False

            expected_signature = HMACSigner.sign_payload(payload, secret_key)
            received_signature_value = signature.split("=", 1)[1]

            if not received_signature_value:
                logger.warning("Пустое значение подписи после 'sha256='")
                return False

            expected_signature_value = expected_signature.split("=", 1)[1]

            is_valid = hmac.compare_digest(expected_signature_value, received_signature_value)

            if not is_valid:
                logger.warning("Подпись не совпадает")

            return is_valid
        except (TypeError, ValueError) as e:
            logger.warning(f"Ошибка при проверке подписи: {e}")
            return False
        except Exception as e:
            logger.warning(f"Неожиданная ошибка при проверке подписи: {e}")
            return False
