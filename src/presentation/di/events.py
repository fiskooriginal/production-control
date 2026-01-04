from typing import Annotated

from fastapi import Depends

from src.application.events.queries.handlers import ListEventsQueryHandler
from src.infrastructure.persistence.queries.events import EventTypeQueryService
from src.presentation.di.common import async_session


async def get_event_type_query_service(
    session: async_session,
) -> EventTypeQueryService:
    """Dependency для EventTypeQueryService"""
    return EventTypeQueryService(session)


event_type_query_service = Annotated[EventTypeQueryService, Depends(get_event_type_query_service)]


async def get_list_events_query_handler(
    query_service: event_type_query_service,
) -> ListEventsQueryHandler:
    """Dependency для ListEventsQueryHandler"""
    return ListEventsQueryHandler(query_service)


list_events = Annotated[ListEventsQueryHandler, Depends(get_list_events_query_handler)]
