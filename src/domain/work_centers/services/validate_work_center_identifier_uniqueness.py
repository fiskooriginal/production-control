from src.domain.work_centers.interfaces.repository import WorkCenterRepositoryProtocol
from src.domain.work_centers.value_objects import WorkCenterIdentifier


async def validate_work_center_identifier_uniqueness(
    identifier: WorkCenterIdentifier, repository: WorkCenterRepositoryProtocol
) -> bool:
    """Проверяет уникальность identifier рабочего центра."""
    existing = await repository.get_by_identifier(identifier.value)
    return existing is None
