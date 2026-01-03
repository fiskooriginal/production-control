from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.common.uow import UnitOfWorkProtocol
from src.core.logging import get_logger
from src.domain.batches.interfaces.repository import BatchRepositoryProtocol
from src.domain.common.events import DomainEvent
from src.domain.products.interfaces.repository import ProductRepositoryProtocol
from src.domain.work_centers.interfaces.repository import WorkCenterRepositoryProtocol
from src.infrastructure.common.uow.event_collector import EventCollector
from src.infrastructure.common.uow.identity_map import IdentityMap
from src.infrastructure.persistence.repositories.batches import BatchRepository
from src.infrastructure.persistence.repositories.outbox import OutboxRepository
from src.infrastructure.persistence.repositories.products import ProductRepository
from src.infrastructure.persistence.repositories.work_centers import WorkCenterRepository

logger = get_logger("uow")


class SqlAlchemyUnitOfWork(UnitOfWorkProtocol):
    """
    Unit of Work для управления транзакциями и сбором доменных событий.

    Критичный lifecycle событий:
    1. flush изменений
    2. собрать события из tracked агрегатов
    3. вставить события в outbox (в той же транзакции)
    4. commit транзакции
    5. ТОЛЬКО после успешного commit: clear_domain_events()

    При rollback события НЕ очищаются.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._identity_map = IdentityMap()
        self._event_collector = EventCollector(self._identity_map)
        self._outbox_repository = OutboxRepository(session)

        self._batch_repo = BatchRepository(session)
        self._product_repo = ProductRepository(session)
        self._work_center_repo = WorkCenterRepository(session)

    @property
    def batches(self) -> BatchRepositoryProtocol:
        """Proxy репозиторий для партий с трекингом агрегатов"""
        return _TrackedRepositoryWrapper(self._batch_repo, self._identity_map)

    @property
    def products(self) -> ProductRepositoryProtocol:
        """Proxy репозиторий для продуктов с трекингом агрегатов"""
        return _TrackedRepositoryWrapper(self._product_repo, self._identity_map)

    @property
    def work_centers(self) -> WorkCenterRepositoryProtocol:
        """Proxy репозиторий для рабочих центров с трекингом агрегатов"""
        return _TrackedRepositoryWrapper(self._work_center_repo, self._identity_map)

    def register_event(self, event: DomainEvent) -> None:
        """
        Регистрирует standalone событие (не привязанное к доменной сущности).
        Используется для регистрации событий в фоновых задачах или сервисном слое.
        """
        self._event_collector.register_event(event)

    async def __aenter__(self) -> Self:
        """Начинает транзакцию UOW"""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """
        Завершает транзакцию UOW.
        При исключении выполняет rollback, события НЕ очищаются.
        """
        if exc_type is not None:
            logger.error(f"Transaction failed with {exc_type.__name__}: {exc_value}")
            await self.rollback()
        else:
            await self.commit()

    async def commit(self) -> None:
        """
        Коммитит транзакцию с сохранением доменных событий в outbox.

        Порядок операций (критично для консистентности):
        1. flush изменений агрегатов
        2. собрать доменные события
        3. вставить события в outbox (в той же транзакции)
        4. commit транзакции
        5. ТОЛЬКО после успешного commit: очистить события у агрегатов
        """
        await self._session.flush()

        outbox_events = self._event_collector.collect_events()

        if outbox_events:
            logger.info(f"Collected {len(outbox_events)} domain event(s)")
            for event in outbox_events:
                logger.debug(f"Event: {event.event_name} v{event.event_version} aggregate_id={event.aggregate_id}")
            await self._outbox_repository.insert_events(outbox_events)

        await self._session.commit()
        logger.info("Transaction committed successfully")

        self._event_collector.clear_events()
        self._identity_map.clear()

    async def rollback(self) -> None:
        """
        Откатывает транзакцию.
        События НЕ очищаются - это позволяет им остаться для retry логики.
        """
        logger.warning("Transaction rolled back")
        await self._session.rollback()
        self._identity_map.clear()


class _TrackedRepositoryWrapper:
    """Wrapper для автоматического трекинга сущностей в IdentityMap"""

    def __init__(self, repository, identity_map: IdentityMap):
        self._repository = repository
        self._identity_map = identity_map

    def __getattr__(self, name: str):
        attr = getattr(self._repository, name)
        if not callable(attr):
            return attr

        async def wrapper(*args, **kwargs):
            result = await attr(*args, **kwargs)

            if hasattr(result, "uuid"):
                self._identity_map.add(result)
            elif isinstance(result, list):
                for entity in result:
                    if hasattr(entity, "uuid"):
                        self._identity_map.add(entity)

            return result

        return wrapper
