from src.infrastructure.events.handlers.decorator import event_handler
from src.infrastructure.events.handlers.registry import EventHandlerRegistry
from src.infrastructure.events.handlers.setup import setup_event_handlers

__all__ = ["EventHandlerRegistry", "event_handler", "setup_event_handlers"]
