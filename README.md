# Hermes Extensions

This repository groups Hermes extensions by type:

| Directory | Contents |
|---|---|
| [`plugins/`](plugins/) | Native Hermes plugins. |
| [`skills/`](skills/) | Standalone Hermes skills. |

## Plugins

| Plugin | Description |
|---|---|
| [`radicale-calendar`](plugins/radicale-calendar/) | Check, create, reschedule, update, and delete appointments through a self-hosted Radicale CalDAV server. |

---

```bash
git clone https://github.com/KingCruzIII/skills.git hermes-plugins
mkdir -p ~/.hermes/plugins
cp -R hermes-plugins/plugins/radicale-calendar ~/.hermes/plugins/radicale-calendar
hermes plugins doctor ~/.hermes/plugins/radicale-calendar --install-deps
```

```bash
hermes plugins enable radicale-calendar
```

`hermes plugins install` prompts for `RADICALE_URL`, `RADICALE_USERNAME`, and
`RADICALE_PASSWORD`; it also offers the optional `RADICALE_TIMEZONE`. Set the
timezone to an IANA name (such as `Europe/Amsterdam` or
`America/New_York`) to accept offset-free local timestamps and return event
timestamps in that timezone.

Hermes currently exposes these manifest fields during plugin installation, not
in the toolset-provider configuration drawer. For a manually copied plugin,
set the values in `~/.hermes/.env` before enabling it:

```dotenv
RADICALE_URL=https://calendar.example.com/
RADICALE_USERNAME=your-username
RADICALE_PASSWORD=your-password
RADICALE_TIMEZONE=America/New_York
```
