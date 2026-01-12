from src.domain.common.queries import PaginationSpec
from src.presentation.exceptions import SerializationException
from src.presentation.v1.common.schemas import PaginationParams


def pagination_params_to_spec(params: PaginationParams) -> PaginationSpec | None:
    """Конвертирует PaginationParams в PaginationSpec"""
    try:
        if params.limit is not None and params.offset is not None:
            return PaginationSpec(limit=params.limit, offset=params.offset)
        return None
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации PaginationParams: {e}") from e
