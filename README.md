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

The plugin installer prompts for `RADICALE_URL`, `RADICALE_USERNAME`, and
`RADICALE_PASSWORD`. Set the optional `RADICALE_TIMEZONE` to an IANA timezone
(such as `Europe/Amsterdam` or `America/New_York`) to accept offset-free local
timestamps and return event timestamps in that timezone.
