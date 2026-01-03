import json

from src.core.logging import get_logger

logger = get_logger("rabbitmq.mapper")


class EventRoutingMapper:
    """Маппинг event_name в routing_key для RabbitMQ"""

    def __init__(self, routing_config: str | None = None) -> None:
        """
        Инициализирует маппер с конфигурацией маршрутизации.

        Args:
            routing_config: JSON строка с маппингом event_name -> routing_key
                           Пример: '{"batch.created": "batch.created", "product.aggregated": "product.aggregated"}'
        """
        self._routing_map: dict[str, str] = {}
        if routing_config:
            try:
                self._routing_map = json.loads(routing_config)
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid routing config JSON: {e}. Using default mapping.")

    def get_routing_key(self, event_name: str) -> str:
        """
        Получает routing_key для event_name.

        Если в конфигурации есть маппинг - использует его,
        иначе использует event_name как routing_key.

        Args:
            event_name: Имя события из EventRegistry

        Returns:
            routing_key для RabbitMQ
        """
        return self._routing_map.get(event_name, event_name)
