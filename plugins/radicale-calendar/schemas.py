"""Model-facing schemas for the Radicale Calendar plugin."""

_CALENDAR = {
    "type": "string",
    "description": "Calendar display name. Required when the account has multiple calendars.",
}

_EVENT_PROPERTIES = {
    "calendar": _CALENDAR,
    "summary": {"type": "string", "description": "Event title."},
    "start": {
        "type": "string",
        "description": (
            "ISO 8601 start datetime, including an offset unless RADICALE_TIMEZONE is configured; "
            "use YYYY-MM-DD when all_day is true."
        ),
    },
    "end": {
        "type": "string",
        "description": (
            "ISO 8601 end datetime, including an offset unless RADICALE_TIMEZONE is configured; "
            "use YYYY-MM-DD when all_day is true. Defaults to the next day for all-day events."
        ),
    },
    "all_day": {
        "type": "boolean",
        "description": "Whether start and end are all-day YYYY-MM-DD values.",
        "default": False,
    },
}

LIST_CALENDARS_SCHEMA = {
    "name": "radicale_list_calendars",
    "description": "List available Radicale CalDAV calendars and their URLs.",
    "parameters": {"type": "object", "properties": {}},
}

LIST_EVENTS_SCHEMA = {
    "name": "radicale_list_events",
    "description": "List events in a Radicale calendar. Defaults to the next seven days.",
    "parameters": {
        "type": "object",
        "properties": {
            "calendar": _CALENDAR,
            "start": _EVENT_PROPERTIES["start"],
            "end": _EVENT_PROPERTIES["end"],
        },
    },
}

CREATE_EVENT_SCHEMA = {
    "name": "radicale_create_event",
    "description": "Create a Radicale calendar event after the user has explicitly confirmed it.",
    "parameters": {
        "type": "object",
        "properties": {
            **_EVENT_PROPERTIES,
            "location": {"type": "string", "description": "Optional event location."},
            "description": {"type": "string", "description": "Optional event description."},
            "recurrence": {
                "type": "string",
                "enum": ["yearly"],
                "description": "Optional recurrence rule for annual events.",
            },
        },
        "required": ["summary", "start"],
    },
}

RESCHEDULE_EVENT_SCHEMA = {
    "name": "radicale_reschedule_event",
    "description": "Change an event's date or time after the user has explicitly confirmed it.",
    "parameters": {
        "type": "object",
        "properties": {
            **_EVENT_PROPERTIES,
            "uid": {
                "type": "string",
                "description": "UID returned by listing or creating the event.",
            },
        },
        "required": ["uid", "start"],
    },
}

UPDATE_EVENT_SCHEMA = {
    "name": "radicale_update_event",
    "description": (
        "Update an event's summary, location, or description after explicit user confirmation."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "uid": {
                "type": "string",
                "description": "UID returned by listing or creating the event.",
            },
            "calendar": _CALENDAR,
            "summary": {"type": "string", "description": "Replacement title; cannot be empty."},
            "location": {
                "type": "string",
                "description": "Replacement location. Pass an empty string to remove it.",
            },
            "description": {
                "type": "string",
                "description": "Replacement description. Pass an empty string to remove it.",
            },
        },
        "required": ["uid"],
    },
}

DELETE_EVENT_SCHEMA = {
    "name": "radicale_delete_event",
    "description": "Delete a Radicale event after the user has explicitly confirmed it.",
    "parameters": {
        "type": "object",
        "properties": {
            "uid": {
                "type": "string",
                "description": "UID returned by listing or creating the event.",
            },
            "calendar": _CALENDAR,
        },
        "required": ["uid"],
    },
}
