from src.domain.batches.interfaces.repository import BatchRepositoryProtocol
from src.domain.batches.value_objects import BatchNumber


async def validate_batch_number_uniqueness(batch_number: BatchNumber, repository: BatchRepositoryProtocol) -> bool:
    """Проверяет уникальность номера партии"""
    existing_batch = await repository.get_by_batch_number(batch_number.value)
    return existing_batch is None
