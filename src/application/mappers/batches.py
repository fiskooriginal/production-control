from src.application.dtos.batches import CreateBatchInputDTO
from src.domain.batches.entities import BatchEntity
from src.domain.batches.value_objects import (
    BatchNumber,
    EknCode,
    Nomenclature,
    Shift,
    ShiftTimeRange,
    TaskDescription,
    Team,
)


def input_dto_to_entity(dto: CreateBatchInputDTO) -> BatchEntity:
    """
    Конвертирует CreateBatchInputDTO в доменную сущность BatchEntity.
    Только конвертация InputDTO → Domain, без бизнес-логики.
    """
    return BatchEntity(
        task_description=TaskDescription(dto.task_description),
        shift=Shift(dto.shift),
        team=Team(dto.team),
        batch_number=BatchNumber(dto.batch_number),
        batch_date=dto.batch_date,
        nomenclature=Nomenclature(dto.nomenclature),
        ekn_code=EknCode(dto.ekn_code),
        shift_time_range=ShiftTimeRange(start=dto.shift_start, end=dto.shift_end),
        products=[],
        work_center_id=dto.work_center_id,
    )
