---
name: calendar-guidance
description: Safely use the Radicale Calendar plugin to list and manage self-hosted CalDAV events.
---

# Radicale Calendar Guidance

Use the `radicale_*` tools to inspect or manage the user's self-hosted
Radicale CalDAV calendar.

## Safety rules

1. Never create, reschedule, update, or delete an event until the user has
   explicitly confirmed the exact change. State the summary, date/time, and
   location before calling a mutating tool.
2. Listing calendars or events needs no confirmation.
3. The only exception is a package-delivery event whose initial tracking was
   explicitly approved: it may be rescheduled when the carrier supplies a new
   estimated date. Notify the user of the old and new dates immediately after.
4. Obtain an event UID from `radicale_list_events` or a create result. Never
   invent a UID.
5. If several calendars exist, call `radicale_list_calendars` and use the
   user's selected display name in every event operation.

## Date and time rules

- Timed `start` and `end` values must be full ISO 8601 timestamps. Include an
  explicit UTC offset unless `RADICALE_TIMEZONE` is configured.
- For all-day events, use bare `YYYY-MM-DD` values with `all_day: true`. The
  end defaults to the following day because iCalendar all-day end dates are
  exclusive.
- Returned timestamps are already converted to `RADICALE_TIMEZONE` when it is
  configured. Do not manually convert them.
