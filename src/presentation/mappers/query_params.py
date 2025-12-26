from datetime import date
from uuid import UUID

from src.application.dtos.batches import BatchFilters
from src.application.dtos.work_centers import WorkCenterFilters
from src.domain.shared.queries import PaginationSpec, SortSpec
from src.presentation.api.schemas.batches import BatchFiltersParams
from src.presentation.api.schemas.query_params import PaginationParams, SortParams
from src.presentation.api.schemas.work_centers import WorkCenterFiltersParams
from src.presentation.exceptions import SerializationException


def pagination_params_to_spec(params: PaginationParams) -> PaginationSpec | None:
    """Конвертирует PaginationParams в PaginationSpec"""
    try:
        if params.limit is not None and params.offset is not None:
            return PaginationSpec(limit=params.limit, offset=params.offset)
        return None
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации PaginationParams: {e}") from e


def sort_params_to_spec(params: SortParams) -> SortSpec | None:
    """Конвертирует SortParams в SortSpec"""
    try:
        if params.sort_field and params.sort_direction:
            return SortSpec(field=params.sort_field, direction=params.sort_direction)
        return None
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации SortParams: {e}") from e


def batch_filters_params_to_dto(params: BatchFiltersParams) -> BatchFilters | None:
    """Конвертирует BatchFiltersParams в BatchFilters DTO"""
    try:
        filter_dict = {}

        if params.is_closed is not None:
            filter_dict["is_closed"] = params.is_closed

        if params.batch_number is not None:
            filter_dict["batch_number"] = params.batch_number

        if params.batch_date:
            filter_dict["batch_date"] = date.fromisoformat(params.batch_date)

        if params.work_center_id:
            filter_dict["work_center_id"] = UUID(params.work_center_id)

        if params.shift:
            filter_dict["shift"] = params.shift

        return BatchFilters(**filter_dict) if filter_dict else None
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации BatchFiltersParams: {e}") from e


def work_center_filters_params_to_dto(params: WorkCenterFiltersParams) -> WorkCenterFilters | None:
    """Конвертирует WorkCenterFiltersParams в WorkCenterFilters DTO"""
    try:
        if params.identifier:
            return WorkCenterFilters(identifier=params.identifier)
        return None
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации WorkCenterFiltersParams: {e}") from e
