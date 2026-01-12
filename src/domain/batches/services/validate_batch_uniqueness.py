from datetime import date
from uuid import UUID

from src.domain.batches.interfaces.repository import BatchRepositoryProtocol
from src.domain.batches.value_objects import BatchNumber


async def is_batch_exist(
    batch_number: BatchNumber,
    batch_date: date,
    repository: BatchRepositoryProtocol,
    exclude_batch_id: UUID | None = None,
) -> bool:
    """Проверяет уникальность комбинации номера партии и даты"""
    existing_batch = await repository.get_by_batch_number_and_date(batch_number.value, batch_date)
    if existing_batch is None:
        return False
    if exclude_batch_id is None:
        return True
    return existing_batch.uuid != exclude_batch_id
