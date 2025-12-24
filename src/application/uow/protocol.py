from abc import abstractmethod
from types import TracebackType
from typing import Protocol, Self

from src.domain.repositories.batches import BatchRepositoryProtocol
from src.domain.repositories.products import ProductRepositoryProtocol
from src.domain.repositories.work_centers import WorkCenterRepositoryProtocol


class UnitOfWorkProtocol(Protocol):
    """
    Протокол UnitOfWork для управления транзакциями и доступа к репозиториям.
    Зависит от domain repository protocols, а не от concrete data.persistence классов.
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
