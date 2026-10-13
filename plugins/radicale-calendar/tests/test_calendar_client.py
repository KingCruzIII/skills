"""Unit tests for Radicale Calendar plugin operations without a live server."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "radicale_calendar",
    ROOT / "__init__.py",
    submodule_search_locations=[str(ROOT)],
)
assert SPEC and SPEC.loader
PACKAGE = importlib.util.module_from_spec(SPEC)
sys.modules["radicale_calendar"] = PACKAGE
SPEC.loader.exec_module(PACKAGE)

from radicale_calendar import (  # noqa: E402
    calendar_client,
    tools,
)


class CalendarClientTests(unittest.TestCase):
    def test_all_day_event_defaults_to_the_following_day(self) -> None:
        event = SimpleNamespace(
            icalendar_component={
                "uid": "event-1",
                "summary": "Birthday",
                "dtstart": SimpleNamespace(dt=date(1990, 4, 13)),
                "dtend": SimpleNamespace(dt=date(1990, 4, 14)),
            }
        )
        calendar = SimpleNamespace(
            get_display_name=lambda: "Personal",
            add_event=lambda **kwargs: event,
        )
        event.parent = calendar
        client = SimpleNamespace(principal=lambda: SimpleNamespace(calendars=lambda: [calendar]))

        with patch.object(calendar_client, "_client", return_value=client):
            result = calendar_client.create_event(
                summary="Birthday",
                start="1990-04-13",
                all_day=True,
                recurrence="yearly",
            )

        self.assertEqual(result["status"], "created")
        self.assertEqual(result["start"], "1990-04-13")
        self.assertEqual(result["end"], "1990-04-14")

    def test_multiple_calendars_require_an_explicit_selection(self) -> None:
        first = SimpleNamespace(get_display_name=lambda: "Personal")
        second = SimpleNamespace(get_display_name=lambda: "Work")
        client = SimpleNamespace(
            principal=lambda: SimpleNamespace(calendars=lambda: [first, second])
        )

        with patch.object(calendar_client, "_client", return_value=client):
            with self.assertRaisesRegex(calendar_client.RadicaleError, "Multiple calendars found"):
                calendar_client.list_events()

    def test_timed_event_without_offset_requires_timezone_configuration(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(calendar_client.RadicaleError, "no timezone offset"):
                calendar_client._parse_datetime("2026-08-15T14:00:00", "start")

    def test_update_rejects_an_empty_summary(self) -> None:
        with self.assertRaisesRegex(calendar_client.RadicaleError, "summary cannot be empty"):
            calendar_client.update_event(uid="event-1", summary="")

    def test_handler_returns_a_json_error_for_missing_configuration(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            result = json.loads(tools.handle_list_calendars({}))

        self.assertIn("Missing required configuration", result["error"])

    def test_registers_all_tools_and_guidance_skill(self) -> None:
        registered_tools: list[str] = []
        registered_skills: list[tuple[str, Path]] = []

        class Context:
            def register_tool(self, **kwargs) -> None:
                registered_tools.append(kwargs["name"])

            def register_skill(self, name: str, path: Path) -> None:
                registered_skills.append((name, path))

        PACKAGE.register(Context())

        self.assertEqual(
            registered_tools,
            [
                "radicale_list_calendars",
                "radicale_list_events",
                "radicale_create_event",
                "radicale_reschedule_event",
                "radicale_update_event",
                "radicale_delete_event",
            ],
        )
        self.assertEqual(registered_skills[0][0], "calendar-guidance")
        self.assertTrue(registered_skills[0][1].is_dir())


if __name__ == "__main__":
    unittest.main()
