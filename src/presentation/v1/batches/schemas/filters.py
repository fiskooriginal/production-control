from typing import Annotated

from fastapi import Query
from pydantic import BaseModel


class BatchFiltersParams(BaseModel):
    """Query параметры для фильтрации партий"""

    is_closed: Annotated[bool | None, Query(description="Фильтр по статусу закрытия")] = None
    batch_number: Annotated[int | None, Query(gt=0, description="Фильтр по номеру партии")] = None
    batch_date: Annotated[str | None, Query(description="Фильтр по дате партии (YYYY-MM-DD)")] = None
    batch_date_from: Annotated[str | None, Query(description="Фильтр по начальной дате партии (YYYY-MM-DD)")] = None
    batch_date_to: Annotated[str | None, Query(description="Фильтр по конечной дате партии (YYYY-MM-DD)")] = None
    work_center_id: Annotated[str | None, Query(description="Фильтр по ID рабочего центра")] = None
    shift: Annotated[str | None, Query(description="Фильтр по смене")] = None
