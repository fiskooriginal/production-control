from src.application.batches.queries.dtos import BatchReadDTO
from src.application.products.queries.dtos import ProductReadDTO
from src.application.work_centers.queries.dtos import WorkCenterReadDTO
from src.presentation.api.schemas.batches import BatchResponse, ShiftTimeRangeSchema
from src.presentation.api.schemas.products import ProductResponse
from src.presentation.api.schemas.work_centers import WorkCenterResponse


def work_center_read_dto_to_response(dto: WorkCenterReadDTO) -> WorkCenterResponse:
    """Конвертирует WorkCenterReadDTO в WorkCenterResponse"""
    return WorkCenterResponse(
        uuid=dto.uuid,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
        identifier=dto.identifier,
        name=dto.name,
    )


def product_read_dto_to_response(dto: ProductReadDTO) -> ProductResponse:
    """Конвертирует ProductReadDTO в ProductResponse"""
    return ProductResponse(
        uuid=dto.uuid,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
        unique_code=dto.unique_code,
        batch_id=dto.batch_id,
        is_aggregated=dto.is_aggregated,
        aggregated_at=dto.aggregated_at,
    )


def batch_read_dto_to_response(dto: BatchReadDTO) -> BatchResponse:
    """Конвертирует BatchReadDTO в BatchResponse"""
    shift_time_range = ShiftTimeRangeSchema(
        start=dto.shift_start,
        end=dto.shift_end,
    )

    products = [
        ProductResponse(
            uuid=p.uuid,
            created_at=p.created_at,
            updated_at=p.updated_at,
            unique_code=p.unique_code,
            batch_id=p.batch_id,
            is_aggregated=p.is_aggregated,
            aggregated_at=p.aggregated_at,
        )
        for p in dto.products
    ]

    return BatchResponse(
        uuid=dto.uuid,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
        is_closed=dto.is_closed,
        closed_at=dto.closed_at,
        task_description=dto.task_description,
        shift=dto.shift,
        team=dto.team,
        batch_number=dto.batch_number,
        batch_date=dto.batch_date,
        nomenclature=dto.nomenclature,
        ekn_code=dto.ekn_code,
        shift_time_range=shift_time_range,
        work_center_id=dto.work_center_id,
        products=products,
    )
