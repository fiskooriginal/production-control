from src.domain.repositories.batches import BatchRepositoryProtocol
from src.domain.repositories.products import ProductRepositoryProtocol
from src.domain.repositories.protocol import BaseRepositoryProtocol
from src.domain.repositories.work_centers import WorkCenterRepositoryProtocol

__all__ = [
    "BaseRepositoryProtocol",
    "BatchRepositoryProtocol",
    "ProductRepositoryProtocol",
    "WorkCenterRepositoryProtocol",
]
