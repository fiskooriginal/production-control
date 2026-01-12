from src.application.events.queries.dtos import EventTypeReadDTO
from src.presentation.v1.events.schemas import EventTypeResponse


def event_type_dto_to_response(dto: EventTypeReadDTO) -> EventTypeResponse:
    """Преобразует EventTypeReadDTO в EventTypeResponse"""
    return EventTypeResponse(
        uuid=dto.uuid,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
        name=dto.name,
        version=dto.version,
        webhook_enabled=dto.webhook_enabled,
        description=dto.description,
    )
