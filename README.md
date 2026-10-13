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
```

Because this repository groups several extensions, copying the plugin does not
run `hermes plugins install` and therefore does not open its install-time
credential prompts. Configure the plugin before enabling it:

```bash
cat >> ~/.hermes/.env <<'EOF'
RADICALE_URL=https://calendar.example.com/
RADICALE_USERNAME=your-username
RADICALE_PASSWORD=your-password
RADICALE_TIMEZONE=America/New_York
EOF

hermes plugins doctor ~/.hermes/plugins/radicale-calendar --install-deps
hermes plugins enable radicale-calendar
```

`RADICALE_TIMEZONE` is optional. Set it to an IANA name (such as
`Europe/Amsterdam` or `America/New_York`) to accept offset-free local
timestamps and return event timestamps in that timezone.

The Hermes toolset-provider drawer shown in the dashboard configures only
provider categories built into Hermes. It cannot render environment settings
for an arbitrary standalone plugin; this plugin reads the configured values
from `~/.hermes/.env` when Hermes starts.
