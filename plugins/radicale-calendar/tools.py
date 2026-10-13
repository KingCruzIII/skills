"""JSON-returning Hermes handlers for the Radicale Calendar plugin."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import caldav

from .calendar_client import (
    RadicaleError,
    create_event,
    delete_event,
    list_calendars,
    list_events,
    reschedule_event,
    update_event,
)


def _handle(operation: Callable[..., object], params: dict[str, Any]) -> str:
    try:
        return json.dumps(operation(**params))
    except (RadicaleError, caldav.error.DAVError) as exc:
        return json.dumps({"error": str(exc)})


def handle_list_calendars(params: dict[str, Any], **_: object) -> str:
    return _handle(list_calendars, params)


def handle_list_events(params: dict[str, Any], **_: object) -> str:
    return _handle(list_events, params)


def handle_create_event(params: dict[str, Any], **_: object) -> str:
    return _handle(create_event, params)


def handle_reschedule_event(params: dict[str, Any], **_: object) -> str:
    return _handle(reschedule_event, params)


def handle_update_event(params: dict[str, Any], **_: object) -> str:
    return _handle(update_event, params)


def handle_delete_event(params: dict[str, Any], **_: object) -> str:
    return _handle(delete_event, params)
