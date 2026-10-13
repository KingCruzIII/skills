"""CalDAV operations used by the Radicale Calendar Hermes plugin."""

from __future__ import annotations

import os
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import caldav


class RadicaleError(ValueError):
    """A user-actionable Radicale configuration or request error."""


def check_requirements() -> bool:
    """Return whether the required Radicale connection settings are configured."""
    return all(
        os.getenv(name) for name in ("RADICALE_URL", "RADICALE_USERNAME", "RADICALE_PASSWORD")
    )


def _client() -> caldav.DAVClient:
    missing = [
        name
        for name in ("RADICALE_URL", "RADICALE_USERNAME", "RADICALE_PASSWORD")
        if not os.getenv(name)
    ]
    if missing:
        raise RadicaleError(f"Missing required configuration: {', '.join(missing)}")
    return caldav.DAVClient(
        url=os.environ["RADICALE_URL"],
        username=os.environ["RADICALE_USERNAME"],
        password=os.environ["RADICALE_PASSWORD"],
    )


def _display_timezone() -> ZoneInfo | None:
    timezone_name = os.getenv("RADICALE_TIMEZONE")
    if not timezone_name:
        return None
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise RadicaleError(
            f"RADICALE_TIMEZONE is not a valid IANA timezone: {timezone_name}"
        ) from exc


def _parse_datetime(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RadicaleError(
            f"{field} must be an ISO 8601 datetime, for example 2026-08-15T14:00:00+02:00"
        ) from exc
    if parsed.tzinfo is not None:
        return parsed
    local_timezone = _display_timezone()
    if local_timezone is None:
        raise RadicaleError(
            f"{field} has no timezone offset. Add an offset or set RADICALE_TIMEZONE "
            "to interpret local timestamps."
        )
    return parsed.replace(tzinfo=local_timezone)


def _parse_date(value: str, field: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise RadicaleError(f"{field} must be a YYYY-MM-DD date for an all-day event") from exc


def _event_interval(
    start_value: str,
    end_value: str | None,
    all_day: bool,
) -> tuple[date | datetime, date | datetime]:
    if all_day:
        start = _parse_date(start_value, "start")
        end = _parse_date(end_value, "end") if end_value else start + timedelta(days=1)
    else:
        if not end_value:
            raise RadicaleError("end is required unless all_day is true")
        start = _parse_datetime(start_value, "start")
        end = _parse_datetime(end_value, "end")
    if end <= start:
        raise RadicaleError("end must be later than start")
    return start, end


def _calendar(principal, name: str | None):
    calendars = principal.calendars()
    if not calendars:
        raise RadicaleError("No calendars exist yet. Create one with a CalDAV client first.")
    if name is None:
        if len(calendars) == 1:
            return calendars[0]
        available = ", ".join(calendar.get_display_name() or "(unnamed)" for calendar in calendars)
        raise RadicaleError(f"Multiple calendars found; pass calendar. Available: {available}")
    for calendar in calendars:
        if calendar.get_display_name() == name:
            return calendar
    available = ", ".join(calendar.get_display_name() or "(unnamed)" for calendar in calendars)
    raise RadicaleError(f"No calendar named '{name}'. Available: {available}")


def _format_datetime(value: date | datetime) -> str:
    if isinstance(value, datetime) and value.tzinfo is not None:
        display_timezone = _display_timezone()
        if display_timezone is not None:
            value = value.astimezone(display_timezone)
    return value.isoformat()


def _event_json(event) -> dict[str, object]:
    component = event.icalendar_component
    start = component.get("dtstart")
    end = component.get("dtend")
    recurrence = component.get("rrule")
    return {
        "uid": str(component.get("uid")),
        "summary": str(component.get("summary", "")),
        "start": _format_datetime(start.dt) if start else None,
        "end": _format_datetime(end.dt) if end else None,
        "location": str(component.get("location", "")) or None,
        "description": str(component.get("description", "")) or None,
        "calendar": event.parent.get_display_name(),
        "all_day": bool(start and not isinstance(start.dt, datetime)),
        "recurring": recurrence.to_ical().decode() if recurrence else None,
    }


def list_calendars() -> list[dict[str, str | None]]:
    principal = _client().principal()
    return [
        {"name": calendar.get_display_name(), "url": str(calendar.url)}
        for calendar in principal.calendars()
    ]


def list_events(
    calendar: str | None = None,
    start: str | None = None,
    end: str | None = None,
) -> list[dict[str, object]]:
    selected_calendar = _calendar(_client().principal(), calendar)
    interval_start = _parse_datetime(start, "start") if start else datetime.now(timezone.utc)
    interval_end = _parse_datetime(end, "end") if end else interval_start + timedelta(days=7)
    if interval_end <= interval_start:
        raise RadicaleError("end must be later than start")
    return [_event_json(event) for event in selected_calendar.search(
        start=interval_start, end=interval_end, event=True, expand=True
    )]


def create_event(
    summary: str,
    start: str,
    end: str | None = None,
    calendar: str | None = None,
    location: str | None = None,
    description: str | None = None,
    all_day: bool = False,
    recurrence: str | None = None,
) -> dict[str, object]:
    if not summary:
        raise RadicaleError("summary cannot be empty")
    selected_calendar = _calendar(_client().principal(), calendar)
    interval_start, interval_end = _event_interval(start, end, all_day)
    attributes: dict[str, object] = {
        "dtstart": interval_start,
        "dtend": interval_end,
        "summary": summary,
    }
    if location:
        attributes["location"] = location
    if description:
        attributes["description"] = description
    if recurrence == "yearly":
        attributes["rrule"] = {"FREQ": "YEARLY"}
    event = selected_calendar.add_event(**attributes)
    return {"status": "created", **_event_json(event)}


def reschedule_event(
    uid: str,
    start: str,
    end: str | None = None,
    calendar: str | None = None,
    all_day: bool = False,
) -> dict[str, object]:
    selected_calendar = _calendar(_client().principal(), calendar)
    event = selected_calendar.event_by_uid(uid)
    if event is None:
        raise RadicaleError(f"No event with uid '{uid}'")
    old_event = _event_json(event)
    interval_start, interval_end = _event_interval(start, end, all_day)
    component = event.icalendar_component
    component["dtstart"].dt = interval_start
    component["dtend"].dt = interval_end
    event.save()
    return {
        "status": "rescheduled",
        "old_start": old_event["start"],
        "old_end": old_event["end"],
        **_event_json(event),
    }


def _set_or_clear(component, field: str, value: str | None) -> None:
    if value is None:
        return
    if value == "":
        if field in component:
            del component[field]
        return
    component[field] = value


def update_event(
    uid: str,
    calendar: str | None = None,
    summary: str | None = None,
    location: str | None = None,
    description: str | None = None,
) -> dict[str, object]:
    if summary is None and location is None and description is None:
        raise RadicaleError("Pass at least one of summary, location, or description")
    if summary == "":
        raise RadicaleError("summary cannot be empty")
    selected_calendar = _calendar(_client().principal(), calendar)
    event = selected_calendar.event_by_uid(uid)
    if event is None:
        raise RadicaleError(f"No event with uid '{uid}'")
    component = event.icalendar_component
    _set_or_clear(component, "summary", summary)
    _set_or_clear(component, "location", location)
    _set_or_clear(component, "description", description)
    event.save()
    return {"status": "updated", **_event_json(event)}


def delete_event(uid: str, calendar: str | None = None) -> dict[str, str]:
    selected_calendar = _calendar(_client().principal(), calendar)
    event = selected_calendar.event_by_uid(uid)
    if event is None:
        raise RadicaleError(f"No event with uid '{uid}'")
    summary = str(event.icalendar_component.get("summary", ""))
    event.delete()
    return {"status": "deleted", "uid": uid, "summary": summary}
