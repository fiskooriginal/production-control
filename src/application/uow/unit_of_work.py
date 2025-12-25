from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.uow.event_collector import EventCollector
from src.application.uow.identity_map import IdentityMap
from src.application.uow.proxy_repositories import (
    BatchRepositoryProxy,
    ProductRepositoryProxy,
    WorkCenterRepositoryProxy,
)
from src.data.persistence.repositories.batches import BatchRepository
from src.data.persistence.repositories.outbox import OutboxRepository
from src.data.persistence.repositories.products import ProductRepository
from src.data.persistence.repositories.work_centers import WorkCenterRepository
from src.domain.batches.repositories import BatchRepositoryProtocol
from src.domain.products.repositories import ProductRepositoryProtocol
from src.domain.work_centers.repositories import WorkCenterRepositoryProtocol


class UnitOfWork:
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

        batch_repo = BatchRepository(session)
        product_repo = ProductRepository(session)
        work_center_repo = WorkCenterRepository(session)

        self._batches = BatchRepositoryProxy(batch_repo, self._identity_map)
        self._products = ProductRepositoryProxy(product_repo, self._identity_map)
        self._work_centers = WorkCenterRepositoryProxy(work_center_repo, self._identity_map)

    @property
    def batches(self) -> BatchRepositoryProtocol:
        """Proxy репозиторий для партий с трекингом агрегатов"""
        return self._batches

    @property
    def products(self) -> ProductRepositoryProtocol:
        """Proxy репозиторий для продуктов с трекингом агрегатов"""
        return self._products

    @property
    def work_centers(self) -> WorkCenterRepositoryProtocol:
        """Proxy репозиторий для рабочих центров с трекингом агрегатов"""
        return self._work_centers

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
            await self._outbox_repository.insert_events(outbox_events)

        await self._session.commit()

        self._event_collector.clear_events()
        self._identity_map.clear()

    async def rollback(self) -> None:
        """
        Откатывает транзакцию.
        События НЕ очищаются - это позволяет им остаться для retry логики.
        """
        await self._session.rollback()
        self._identity_map.clear()
