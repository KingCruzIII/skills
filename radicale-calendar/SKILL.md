---
name: radicale-calendar
description: "Check, create, reschedule, and delete calendar appointments and tracked package deliveries via Radicale (self-hosted CalDAV)."
version: 1.0.0
author: KingCruzIII
license: MIT
platforms: [linux, macos, windows]
required_environment_variables:
  - name: RADICALE_URL
    prompt: Base URL of your Radicale server (e.g. https://calendar.example.com/)
    help: "The CalDAV root URL Radicale serves from - same one you'd enter in any CalDAV client."
  - name: RADICALE_USERNAME
    prompt: Radicale account username
  - name: RADICALE_PASSWORD
    prompt: Radicale account password
    help: "Basic auth password (or an app password, if Radicale sits behind a reverse proxy that enforces one)."
metadata:
  hermes:
    tags: [Calendar, CalDAV, Radicale, Scheduling, Package Tracking, Deliveries]
    homepage: https://radicale.org
---

# Radicale Calendar

Check, create, reschedule, and delete appointments on a self-hosted
[Radicale](https://radicale.org) CalDAV calendar via a small CLI wrapper
(`scripts/radicale_cli.py`) around the `caldav` Python library. Talks
directly to your own Radicale server - not a public cloud calendar, no
OAuth flow, just a URL + basic auth.

## Prerequisites

Install this skill's own venv, then point it at your Radicale instance:

```bash
cd <skill-install-dir>
uv venv .venv && uv pip install --python .venv/bin/python -e .
cp .env.example .env   # then fill in RADICALE_URL / RADICALE_USERNAME / RADICALE_PASSWORD
```

Script and skill docs live together in this one directory (venv, `.env`,
`scripts/`) rather than split across separate tool/doc paths - keeps the
whole thing self-contained and easy to relocate.

Also set `RADICALE_TIMEZONE` in `.env` to your own IANA timezone name
(e.g. `Europe/Amsterdam`, `America/New_York`) - strongly recommended. It
converts returned timestamps to your local time and lets the CLI interpret
local input without a UTC offset. Without it, use explicit offsets such as
`2026-08-15T14:00:00-04:00` for every timed input; the CLI rejects ambiguous
timezone-less times.

## When to Use

- "What's on my calendar [today / this week / on X date]?"
- "Do I have anything on [date/time]?" (check for conflicts before agreeing to something)
- "Add an appointment for..." / "Schedule a meeting..."
- "Move my [X] appointment to..." / "Reschedule..."
- "Cancel my [X] appointment"
- "Add my package delivery to the calendar" / "When is my package arriving?"

## Common Commands

Always run via the venv's own interpreter, from the tool's directory:

```bash
cd <skill-install-dir>
.venv/bin/python scripts/radicale_cli.py <command> [args]
```

All commands return JSON on stdout. Parse it, don't eyeball raw text.

### List calendars

```bash
.venv/bin/python scripts/radicale_cli.py list-calendars
```

### List events (defaults to the next 7 days if no --start/--end given)

```bash
.venv/bin/python scripts/radicale_cli.py list-events
.venv/bin/python scripts/radicale_cli.py list-events --start 2026-08-12T00:00:00 --end 2026-08-19T00:00:00
```

Returns `[{uid, summary, start, end, location, description, calendar}]`.
When there is more than one calendar, add `--calendar "<calendar name>"` to
every event command; the CLI refuses to guess.

### Create an event

```bash
.venv/bin/python scripts/radicale_cli.py create-event \
  --summary "Dentist" --start 2026-08-15T14:00:00 --end 2026-08-15T15:00:00 \
  --location "Downtown Clinic" --description "Check-up"
```

Returns `{status: "created", uid, summary, start, end, ...}` - the `uid` is
needed for rescheduling/deleting later.

### Track an expected package delivery

Create a distinct, all-day event on the carrier's estimated delivery date.
Use the package or merchant name in the summary and keep the carrier and
tracking number in the description so Hermes can reliably find the event
again. Confirm the initial calendar entry with the user before creating it.

```bash
.venv/bin/python scripts/radicale_cli.py create-event \
  --summary "Package delivery: USB-C charger" --start 2026-08-15 --all-day \
  --description "Carrier: UPS; tracking: 1Z999AA10123456784; estimated delivery"
```

Save the returned `uid` with the package's tracking record. If a carrier
subsequently changes the delivery date, Hermes may reschedule that known
delivery event without asking again:

```bash
.venv/bin/python scripts/radicale_cli.py reschedule-event \
  --uid <saved-package-event-uid> --start 2026-08-16 --all-day
```

After an automatic reschedule, notify the user through Hermes' available
notification mechanism. If no separate notification mechanism is available,
state the old and new delivery dates in the current response. This skill
does not poll carriers or send notifications itself; a tracking integration
must supply delivery updates and Hermes must retain the event `uid`.

### Create an all-day / recurring event (e.g. a birthday or anniversary)

```bash
.venv/bin/python scripts/radicale_cli.py create-event \
  --summary "🎂 Someone's Birthday" --start 1990-04-13 --all-day --recur yearly
```

`--all-day` takes a bare `YYYY-MM-DD` (no time) and produces a proper
whole-day event (`DTSTART;VALUE=DATE`, not a timed one) - `--end` defaults to
the day after `--start` if omitted (iCal's DTEND is exclusive, so a
single-day all-day event's end is technically the next day). `--recur
yearly` adds `RRULE:FREQ=YEARLY` - `list-events` correctly expands it into
future years without needing to re-create the event annually.

Tip: for recurring personal dates (birthdays, anniversaries) where the real
year matters for age math elsewhere, set `--start`'s year to the real one
and use `--description` as a marker your own automation can check (e.g.
`"birth year known"` vs `"birth year unknown"` if you use a placeholder
year) - events here are name-only, no age is shown or computed by this
skill itself.

### Reschedule an event (change when it happens)

```bash
.venv/bin/python scripts/radicale_cli.py reschedule-event \
  --uid <uid-from-list-or-create> --start 2026-08-16T14:00:00 --end 2026-08-16T15:00:00
```

**Note the naming**: this is `reschedule-event`, not `move-event` -
deliberately, to avoid ambiguity with other CalDAV tools where "move" means
transferring an event to a *different calendar*. This changes the
date/time only.

### Update other fields (summary/location/description, not the time)

```bash
.venv/bin/python scripts/radicale_cli.py update-event --uid <uid> --location "New location"
```

Pass an empty string (`--location ""`) to clear a field entirely rather
than leaving it set.

### Delete an event

```bash
.venv/bin/python scripts/radicale_cli.py delete-event --uid <uid>
```

## Rules

1. **Never create, reschedule, or delete an event without confirming with
   the user first.** Show what will be created/changed/removed (summary,
   date/time, location) and get explicit confirmation before running the
   command. Listing/checking events needs no confirmation. **Exception:**
   after the user has approved tracking a package delivery, Hermes may
   automatically reschedule that package's known event when its carrier
   changes the estimated delivery date. It must then notify the user of the
   old and new dates.
2. **Always include a date and an ISO 8601 timestamp** for timed
   `--start`/`--end`. Include an explicit offset unless `RADICALE_TIMEZONE`
   is configured, in which case an offset-free value is interpreted in that
   timezone. If a time is given without a date, resolve the actual date
   before calling anything (check today's date, don't guess).
2b. **Returned `start`/`end` values are already in local time if
   `RADICALE_TIMEZONE` is set - no manual conversion needed.** The CLI
   itself converts every returned timestamp before you ever see it; just
   read the value as-is. If `RADICALE_TIMEZONE` is unset, values stay in
   UTC with an explicit offset (e.g. `12:00:00+00:00`) - in that case,
   either mention you're reporting UTC when speaking a time to the user,
   or (better) go set `RADICALE_TIMEZONE` in `.env` so this stops being a
   manual thing to remember. Don't try to convert a timestamp "by hand"
   from what you assume the user's timezone is - that's exactly the
   failure mode this setting exists to remove.
3. **Get the `uid` from `list-events` or `create-event`'s own output**
   before rescheduling/updating/deleting - don't guess or invent one.
4. **If only one calendar exists**, commands default to it and no
   `--calendar` flag is needed. Once more than one calendar exists, check
   `list-calendars` first and pass the chosen calendar name with
   `--calendar`; the CLI refuses to assume which one is meant.
