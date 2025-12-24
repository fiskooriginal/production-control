from abc import abstractmethod
from types import TracebackType
from typing import Protocol, Self

from src.data.persistence.repositories.batches import BatchRepository
from src.data.persistence.repositories.products import ProductRepository
from src.data.persistence.repositories.work_centers import WorkCenterRepository
from src.domain.repositories.protocol import BaseRepositoryProtocol


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

    @property
    @abstractmethod
    def repository(self) -> BaseRepositoryProtocol: ...

    @property
    @abstractmethod
    def batches(self) -> BatchRepository: ...

    @property
    @abstractmethod
    def products(self) -> ProductRepository: ...

    @property
    @abstractmethod
    def work_centers(self) -> WorkCenterRepository: ...
