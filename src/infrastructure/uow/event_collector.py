from uuid import uuid4

from src.core.time import datetime_aware_to_naive, datetime_now
from src.domain.common.events import DomainEvent
from src.infrastructure.persistence.models.outbox_event import OutboxEvent, OutboxEventStatusEnum
from src.infrastructure.uow.identity_map import IdentityMap


def generate_dedup_key(event: DomainEvent) -> str:
    """
    Генерирует ключ дедупликации для события.
    Формат: event_name:aggregate_id:occurred_at_iso
    """
    from src.infrastructure.events import EventRegistry

    event_name, _ = EventRegistry.get_event_metadata(type(event))
    occurred_at_str = event.occurred_at.isoformat()
    return f"{event_name}:{event.aggregate_id}:{occurred_at_str}"


class EventCollector:
    """
    Собирает доменные события из отслеживаемых агрегатов и преобразует их в OutboxEvent.
    Работает совместно с IdentityMap для извлечения событий из всех агрегатов в рамках UOW.
    """

    def __init__(self, identity_map: IdentityMap) -> None:
        self._identity_map = identity_map

    def collect_events(self) -> list[OutboxEvent]:
        """
        Собирает все доменные события из tracked агрегатов и преобразует в OutboxEvent.
        События НЕ очищаются здесь - это делается после успешного commit.
        """
        outbox_events: list[OutboxEvent] = []

        for entity in self._identity_map.get_all():
            domain_events = entity.get_domain_events()
            for domain_event in domain_events:
                outbox_event = self._convert_to_outbox(domain_event)
                outbox_events.append(outbox_event)

        return outbox_events

    def clear_events(self) -> None:
        """
        Очищает доменные события у всех tracked агрегатов.
        Вызывается ТОЛЬКО после успешного commit транзакции.
        """
        for entity in self._identity_map.get_all():
            entity.clear_domain_events()

    def _convert_to_outbox(self, event: DomainEvent) -> OutboxEvent:
        """Преобразует доменное событие в OutboxEvent для сохранения в БД"""
        from src.infrastructure.events import EventSerializer

        serialized = EventSerializer.serialize(event)

        dedup_key = generate_dedup_key(event)

        return OutboxEvent(
            uuid=uuid4(),
            event_name=serialized["event_name"],
            event_version=serialized["event_version"],
            aggregate_id=event.aggregate_id,
            payload=serialized["payload"],
            occurred_at=datetime_aware_to_naive(event.occurred_at),
            created_at=datetime_aware_to_naive(datetime_now()),
            status=OutboxEventStatusEnum.PENDING,
            attempts=0,
            dedup_key=dedup_key,
        )
