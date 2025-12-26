from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.exceptions import DatabaseException
from src.infrastructure.persistence.models.outbox_event import OutboxEvent, OutboxEventStatus


class OutboxRepository:
    """Репозиторий для работы с Transactional Outbox"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def insert_event(self, event: OutboxEvent) -> OutboxEvent:
        """Вставляет событие в outbox в рамках текущей транзакции"""
        try:
            self._session.add(event)
            await self._session.flush()
            return event
        except DBAPIError as e:
            raise DatabaseException(f"Ошибка базы данных при вставке события в outbox: {e}") from e
        except SQLAlchemyError as e:
            raise DatabaseException(f"Ошибка SQLAlchemy при вставке события в outbox: {e}") from e

    async def insert_events(self, events: list[OutboxEvent]) -> list[OutboxEvent]:
        """Вставляет несколько событий в outbox в рамках текущей транзакции"""
        try:
            self._session.add_all(events)
            await self._session.flush()
            return events
        except DBAPIError as e:
            raise DatabaseException(f"Ошибка базы данных при вставке событий в outbox: {e}") from e
        except SQLAlchemyError as e:
            raise DatabaseException(f"Ошибка SQLAlchemy при вставке событий в outbox: {e}") from e

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
            now = datetime.now(UTC)
            locked_until = now + timedelta(seconds=lock_duration_seconds)

            stmt = (
                select(OutboxEvent)
                .where(
                    OutboxEvent.status == OutboxEventStatus.PENDING,
                    (OutboxEvent.locked_until == None) | (OutboxEvent.locked_until < now),  # noqa: E711
                )
                .order_by(OutboxEvent.created_at)
                .limit(limit)
                .with_for_update(skip_locked=True)
            )

            result = await self._session.execute(stmt)
            events = list(result.scalars().all())

            for event in events:
                event.status = OutboxEventStatus.PROCESSING
                event.locked_until = locked_until
                event.attempts += 1
                event.updated_at = now

            await self._session.flush()
            return events
        except DBAPIError as e:
            raise DatabaseException(f"Ошибка базы данных при захвате событий из outbox: {e}") from e
        except SQLAlchemyError as e:
            raise DatabaseException(f"Ошибка SQLAlchemy при захвате событий из outbox: {e}") from e

    async def mark_event_done(self, event_id: UUID) -> None:
        """Отмечает событие как успешно обработанное (для будущего воркера)"""
        try:
            now = datetime.now(UTC)
            event = await self._session.get(OutboxEvent, event_id)
            if event:
                event.status = OutboxEventStatus.DONE
                event.processed_at = now
                event.locked_until = None
                event.updated_at = now
                await self._session.flush()
        except DBAPIError as e:
            raise DatabaseException(f"Ошибка базы данных при отметке события как выполненного: {e}") from e
        except SQLAlchemyError as e:
            raise DatabaseException(f"Ошибка SQLAlchemy при отметке события как выполненного: {e}") from e

    async def mark_event_failed(self, event_id: UUID, error: str) -> None:
        """Отмечает событие как неудачно обработанное (для будущего воркера)"""
        try:
            now = datetime.now(UTC)
            event = await self._session.get(OutboxEvent, event_id)
            if event:
                event.status = OutboxEventStatus.FAILED
                event.last_error = error
                event.locked_until = None
                event.updated_at = now
                await self._session.flush()
        except DBAPIError as e:
            raise DatabaseException(f"Ошибка базы данных при отметке события как неудачного: {e}") from e
        except SQLAlchemyError as e:
            raise DatabaseException(f"Ошибка SQLAlchemy при отметке события как неудачного: {e}") from e

    async def retry_failed_event(self, event_id: UUID) -> None:
        """Возвращает failed событие обратно в pending для повторной обработки (для будущего воркера)"""
        try:
            now = datetime.now(UTC)
            event = await self._session.get(OutboxEvent, event_id)
            if event and event.status == OutboxEventStatus.FAILED:
                event.status = OutboxEventStatus.PENDING
                event.locked_until = None
                event.updated_at = now
                await self._session.flush()
        except DBAPIError as e:
            raise DatabaseException(f"Ошибка базы данных при повторной обработке события: {e}") from e
        except SQLAlchemyError as e:
            raise DatabaseException(f"Ошибка SQLAlchemy при повторной обработке события: {e}") from e
