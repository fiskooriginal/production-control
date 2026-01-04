from fastapi import APIRouter, status

from src.presentation.api.schemas.events import ListEventsResponse
from src.presentation.di.events import list_events
from src.presentation.mappers.events import event_type_dto_to_response

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("", response_model=ListEventsResponse, status_code=status.HTTP_200_OK)
async def get_events(query_handler: list_events) -> ListEventsResponse:
    """
    Получает список всех актуальных типов событий системы.
    """
    dtos = await query_handler.execute()
    return ListEventsResponse(items=[event_type_dto_to_response(dto) for dto in dtos])
