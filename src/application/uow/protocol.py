from abc import abstractmethod
from types import TracebackType
from typing import Protocol, Self

from src.domain.batches.interfaces.repository import BatchRepositoryProtocol
from src.domain.products.interfaces.repository import ProductRepositoryProtocol
from src.domain.work_centers.interfaces.repository import WorkCenterRepositoryProtocol


class UnitOfWorkProtocol(Protocol):
    """
    Протокол UnitOfWork для управления транзакциями и доступа к репозиториям.
    Зависит от domain repository protocols, а не от concrete infrastructure.persistence классов.
    """

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

    @property
    @abstractmethod
    def batches(self) -> BatchRepositoryProtocol: ...

    @property
    @abstractmethod
    def products(self) -> ProductRepositoryProtocol: ...

    @property
    @abstractmethod
    def work_centers(self) -> WorkCenterRepositoryProtocol: ...
