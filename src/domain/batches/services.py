from src.domain.batches.entities import BatchEntity
from src.domain.batches.value_objects import BatchNumber
from src.domain.repositories.batches import BatchRepositoryProtocol


async def validate_batch_number_uniqueness(batch_number: BatchNumber, repository: BatchRepositoryProtocol) -> bool:
    """Проверяет уникальность номера партии"""
    existing_batch = await repository.get_by_batch_number(batch_number.value)
    return existing_batch is None


async def validate_shift_time_overlap(batch: BatchEntity, repository: BatchRepositoryProtocol) -> bool:
    """Проверяет пересечение времени смены с другими партиями"""
    batches = await repository.get_by_work_center(batch.work_center_id)
    for other_batch in batches:
        if other_batch.uuid == batch.uuid:
            continue
        if (
            batch.shift_time_range.start < other_batch.shift_time_range.end
            and batch.shift_time_range.end > other_batch.shift_time_range.start
        ):
            return False
    return True


def can_close_batch(batch: BatchEntity) -> bool:
    """Проверяет, можно ли закрыть партию"""
    if batch.is_closed:
        return False
    if not batch.products:
        return False
    all_aggregated = all(product.is_aggregated for product in batch.products)
    return all_aggregated
