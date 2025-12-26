from src.domain.batches.entities import BatchEntity
from src.domain.batches.interfaces.repository import BatchRepositoryProtocol


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
