from abc import abstractmethod
from types import TracebackType
from typing import Protocol, Self

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
