from src.application.batches.queries import BatchReadDTO, ProductReadDTONested
from src.infrastructure.persistence.models.batch import Batch


def batch_model_to_read_dto(model: Batch) -> BatchReadDTO:
    """Преобразует модель SQLAlchemy в BatchReadDTO"""
    products_dto = [
        ProductReadDTONested(
            uuid=p.uuid,
            created_at=p.created_at,
            updated_at=p.updated_at,
            unique_code=p.unique_code,
            batch_id=p.batch_id,
            is_aggregated=p.is_aggregated,
            aggregated_at=p.aggregated_at,
        )
        for p in model.products
    ]

    return BatchReadDTO(
        uuid=model.uuid,
        created_at=model.created_at,
        updated_at=model.updated_at,
        is_closed=model.is_closed,
        closed_at=model.closed_at,
        task_description=model.task_description,
        shift=model.shift,
        team=model.team,
        batch_number=model.batch_number,
        batch_date=model.batch_date,
        nomenclature=model.nomenclature,
        ekn_code=model.ekn_code,
        shift_start=model.shift_start_time,
        shift_end=model.shift_end_time,
        work_center_id=model.work_center_id,
        products=products_dto,
    )
