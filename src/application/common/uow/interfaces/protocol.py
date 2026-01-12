from abc import abstractmethod
from types import TracebackType
from typing import Protocol, Self

from src.domain.batches.interfaces.repository import BatchRepositoryProtocol
from src.domain.common.events import DomainEvent
from src.domain.products.interfaces.repository import ProductRepositoryProtocol
from src.domain.webhooks.interfaces.delivery import WebhookDeliveryRepositoryProtocol
from src.domain.webhooks.interfaces.subscription import WebhookSubscriptionRepositoryProtocol
from src.domain.work_centers.interfaces.repository import WorkCenterRepositoryProtocol


class UnitOfWorkProtocol(Protocol):
    @abstractmethod
    async def __aenter__(self) -> Self: ...

    @abstractmethod
    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None
    ) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

    def register_event(self, event: DomainEvent) -> None:
        """
        Регистрирует standalone событие (не привязанное к доменной сущности).
        Используется для регистрации событий в фоновых задачах или сервисном слое.
        """
        ...

    @property
    @abstractmethod
    def batches(self) -> BatchRepositoryProtocol: ...

    @property
    @abstractmethod
    def products(self) -> ProductRepositoryProtocol: ...

    @property
    @abstractmethod
    def work_centers(self) -> WorkCenterRepositoryProtocol: ...

    @property
    @abstractmethod
    def webhook_subscriptions(self) -> WebhookSubscriptionRepositoryProtocol: ...

    @property
    @abstractmethod
    def webhook_deliveries(self) -> WebhookDeliveryRepositoryProtocol: ...
