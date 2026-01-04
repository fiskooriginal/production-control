from datetime import timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.time import datetime_now
from src.infrastructure.common.exceptions import OutboxRepositoryException
from src.infrastructure.persistence.models.outbox_event import OutboxEvent, OutboxEventStatusEnum


class OutboxRepository:
    """Репозиторий для работы с Transactional Outbox"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def insert_events(self, events: list[OutboxEvent]) -> list[OutboxEvent]:
        """Вставляет несколько событий в outbox в рамках текущей транзакции"""
        try:
            self._session.add_all(events)
            await self._session.flush()
            return events
        except Exception as e:
            raise OutboxRepositoryException(f"Ошибка при вставке событий в outbox: {e}") from e

    async def claim_pending_events(
        self,
        limit: int = 100,
        lock_duration_seconds: int = 300,
    ) -> list[OutboxEvent]:
        """
        Захватывает pending события для обработки (для будущего воркера).
        Использует FOR UPDATE SKIP LOCKED для конкурентной обработки.
        """
        try:
            now = datetime_now(naive=True)
            locked_until = now + timedelta(seconds=lock_duration_seconds)

            stmt = (
                select(OutboxEvent)
                .where(
                    OutboxEvent.status == OutboxEventStatusEnum.PENDING,
                    (OutboxEvent.locked_until is None) | (OutboxEvent.locked_until < now),
                )
                .order_by(OutboxEvent.created_at)
                .limit(limit)
                .with_for_update(skip_locked=True)
            )

            result = await self._session.execute(stmt)
            events = list(result.scalars().all())

            for event in events:
                event.status = OutboxEventStatusEnum.PROCESSING
                event.attempts += 1
                event.locked_until = locked_until
                event.updated_at = now

            await self._session.flush()
            return events
        except Exception as e:
            raise OutboxRepositoryException(f"Ошибка при захвате событий из outbox: {e}") from e

    async def mark_event_done(self, event_id: UUID) -> None:
        """Отмечает событие как успешно обработанное (для будущего воркера)"""
        try:
            now = datetime_now(naive=True)
            event = await self._session.get(OutboxEvent, event_id)
            if event:
                event.status = OutboxEventStatusEnum.DONE
                event.locked_until = None
                event.processed_at = now
                event.updated_at = now
            await self._session.flush()
        except Exception as e:
            raise OutboxRepositoryException(f"Ошибка при отметке события как выполненного: {e}") from e

    async def mark_event_failed(self, event_id: UUID, error: str) -> None:
        """Отмечает событие как неудачно обработанное (для будущего воркера)"""
        try:
            now = datetime_now(naive=True)
            event = await self._session.get(OutboxEvent, event_id)
            if event:
                event.status = OutboxEventStatusEnum.FAILED
                event.last_error = error
                event.locked_until = None
                event.updated_at = now
            await self._session.flush()
        except Exception as e:
            raise OutboxRepositoryException(f"Ошибка при отметке события как неудачного: {e}") from e

    async def retry_failed_event(self, event_id: UUID) -> None:
        """Возвращает failed событие обратно в pending для повторной обработки (для будущего воркера)"""
        try:
            now = datetime_now(naive=True)
            event = await self._session.get(OutboxEvent, event_id)
            if event and event.status == OutboxEventStatusEnum.FAILED:
                event.status = OutboxEventStatusEnum.PENDING
                event.locked_until = None
                event.updated_at = now
            await self._session.flush()
        except Exception as e:
            raise OutboxRepositoryException(f"Ошибка при повторной обработке события: {e}") from e
