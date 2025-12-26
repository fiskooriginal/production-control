import builtins
from uuid import UUID

from src.application.uow.identity_map import IdentityMap
from src.domain.batches.entities import BatchEntity
from src.domain.batches.interfaces.repository import BatchRepositoryProtocol
from src.domain.products.entities import ProductEntity
from src.domain.products.interfaces.repository import ProductRepositoryProtocol
from src.domain.work_centers.entities import WorkCenterEntity
from src.domain.work_centers.interfaces.repository import WorkCenterRepositoryProtocol
from src.infrastructure.persistence.repositories.batches import BatchRepository
from src.infrastructure.persistence.repositories.products import ProductRepository
from src.infrastructure.persistence.repositories.work_centers import WorkCenterRepository


class BatchRepositoryProxy(BatchRepositoryProtocol):
    """
    Proxy поверх BatchRepository который регистрирует агрегаты в IdentityMap.
    Не изменяет оригинальный infrastructure.persistence репозиторий.
    """

    def __init__(self, repository: BatchRepository, identity_map: IdentityMap) -> None:
        self._repository = repository
        self._identity_map = identity_map

    async def create(self, domain_entity: BatchEntity) -> BatchEntity:
        result = await self._repository.create(domain_entity)
        self._identity_map.add(result)
        return result

    async def get_or_raise(self, uuid: UUID) -> BatchEntity:
        result = await self._repository.get_or_raise(uuid)
        self._identity_map.add(result)
        return result

    async def update(self, domain_entity: BatchEntity) -> BatchEntity:
        result = await self._repository.update(domain_entity)
        self._identity_map.add(result)
        return result

    async def delete(self, uuid: UUID) -> None:
        await self._repository.delete(uuid)

    async def get_by_batch_number(self, batch_number: int) -> BatchEntity | None:
        result = await self._repository.get_by_batch_number(batch_number)
        if result:
            self._identity_map.add(result)
        return result

    async def get_by_work_center(self, work_center_uuid: UUID) -> builtins.list[BatchEntity]:
        results = await self._repository.get_by_work_center(work_center_uuid)
        for entity in results:
            self._identity_map.add(entity)
        return results


class ProductRepositoryProxy(ProductRepositoryProtocol):
    """
    Proxy поверх ProductRepository который регистрирует агрегаты в IdentityMap.
    """

    def __init__(self, repository: ProductRepository, identity_map: IdentityMap) -> None:
        self._repository = repository
        self._identity_map = identity_map

    async def create(self, domain_entity: ProductEntity) -> ProductEntity:
        result = await self._repository.create(domain_entity)
        self._identity_map.add(result)
        return result

    async def get_or_raise(self, uuid: UUID) -> ProductEntity:
        result = await self._repository.get_or_raise(uuid)
        self._identity_map.add(result)
        return result

    async def update(self, domain_entity: ProductEntity) -> ProductEntity:
        result = await self._repository.update(domain_entity)
        self._identity_map.add(result)
        return result

    async def delete(self, uuid: UUID) -> None:
        await self._repository.delete(uuid)

    async def get_by_unique_code(self, unique_code: str) -> ProductEntity | None:
        result = await self._repository.get_by_unique_code(unique_code)
        if result:
            self._identity_map.add(result)
        return result

    async def get_aggregated(self) -> builtins.list[ProductEntity]:
        results = await self._repository.get_aggregated()
        for entity in results:
            self._identity_map.add(entity)
        return results

    async def get_by_ids(self, product_ids: builtins.list[UUID]) -> builtins.list[ProductEntity]:
        results = await self._repository.get_by_ids(product_ids)
        for entity in results:
            self._identity_map.add(entity)
        return results


class WorkCenterRepositoryProxy(WorkCenterRepositoryProtocol):
    """
    Proxy поверх WorkCenterRepository который регистрирует агрегаты в IdentityMap.
    """

    def __init__(self, repository: WorkCenterRepository, identity_map: IdentityMap) -> None:
        self._repository = repository
        self._identity_map = identity_map

    async def create(self, domain_entity: WorkCenterEntity, author: UUID | None = None) -> WorkCenterEntity:
        result = await self._repository.create(domain_entity, author=author)
        self._identity_map.add(result)
        return result

    async def get_or_raise(self, uuid: UUID) -> WorkCenterEntity:
        result = await self._repository.get_or_raise(uuid)
        self._identity_map.add(result)
        return result

    async def update(self, domain_entity: WorkCenterEntity) -> WorkCenterEntity:
        result = await self._repository.update(domain_entity)
        self._identity_map.add(result)
        return result

    async def delete(self, uuid: UUID) -> None:
        await self._repository.delete(uuid)

    async def get_by_identifier(self, identifier: str) -> WorkCenterEntity | None:
        result = await self._repository.get_by_identifier(identifier)
        if result:
            self._identity_map.add(result)
        return result
