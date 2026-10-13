"""Hermes plugin for self-hosted Radicale CalDAV calendars."""

from __future__ import annotations

from pathlib import Path

from .calendar_client import check_requirements
from .schemas import (
    CREATE_EVENT_SCHEMA,
    DELETE_EVENT_SCHEMA,
    LIST_CALENDARS_SCHEMA,
    LIST_EVENTS_SCHEMA,
    RESCHEDULE_EVENT_SCHEMA,
    UPDATE_EVENT_SCHEMA,
)
from .tools import (
    handle_create_event,
    handle_delete_event,
    handle_list_calendars,
    handle_list_events,
    handle_reschedule_event,
    handle_update_event,
)

_TOOLS = (
    ("radicale_list_calendars", LIST_CALENDARS_SCHEMA, handle_list_calendars),
    ("radicale_list_events", LIST_EVENTS_SCHEMA, handle_list_events),
    ("radicale_create_event", CREATE_EVENT_SCHEMA, handle_create_event),
    ("radicale_reschedule_event", RESCHEDULE_EVENT_SCHEMA, handle_reschedule_event),
    ("radicale_update_event", UPDATE_EVENT_SCHEMA, handle_update_event),
    ("radicale_delete_event", DELETE_EVENT_SCHEMA, handle_delete_event),
)

_REQUIRED_ENV = ("RADICALE_URL", "RADICALE_USERNAME", "RADICALE_PASSWORD")


def register(ctx) -> None:
    """Register Radicale calendar tools and their operating guidance."""
    for name, schema, handler in _TOOLS:
        ctx.register_tool(
            name=name,
            toolset="radicale_calendar",
            schema=schema,
            handler=handler,
            check_fn=check_requirements,
            requires_env=list(_REQUIRED_ENV),
        )
    ctx.register_skill("calendar-guidance", Path(__file__).parent / "skills" / "calendar-guidance")
