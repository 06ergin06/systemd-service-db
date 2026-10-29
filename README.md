# systemd Service DB

**English** | [Turkish](README.tr.md)

[![Validate data](https://github.com/06ergin06/systemd-service-db/actions/workflows/validate.yml/badge.svg)](https://github.com/06ergin06/systemd-service-db/actions/workflows/validate.yml)
[![Sync data](https://github.com/06ergin06/systemd-service-db/actions/workflows/sync.yml/badge.svg)](https://github.com/06ergin06/systemd-service-db/actions/workflows/sync.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![JSON Schema: Draft 2020-12](https://img.shields.io/badge/JSON%20Schema-Draft%202020--12-green)](schemas/)

A central, bilingual, validated systemd service database for
[`pardus-boot-analyzer`](https://github.com/06ergin06/pardus-boot-analyzer) and
[`linux_boot_analyzer_tui`](https://github.com/06ergin06/linux_boot_analyzer_tui).

**147 services · 3 profiles · JSON Schema · dependency-free validator · auto-sync**

## Layout

```text
data/services.json       # keyed by unit name
data/profiles.json       # Office, Developer, Minimum
schemas/                 # JSON Schema Draft 2020-12
scripts/validate.py      # syntax, schema, reference and sort checks
scripts/export_legacy.py # compatibility adapter for the existing apps
.github/workflows/       # validate.yml, sync.yml
```

## Data

The canonical data uses English identifiers only. Localized text is stored as
values, while every object key, field name, profile identifier, and enum value
is English.

Each service in `data/services.json` contains:

- `name`
- `description_tr`, `description_en`
- `suggestion_tr`, `suggestion_en`
- `category`, `safe_to_disable`, `critical`, `required`

The canonical classification is expressed by the three booleans:

| Classification | `safe_to_disable` | `critical` | `required` |
|---|---:|---:|---:|
| Discretionary | `true` | `false` | `false` |
| Critical | `false` | `true` | `false` |
| Required | `false` | `false` | `true` |

Categories: `system`, `boot`, `network`, `bluetooth`, `printing`, `telemetry`,
`storage`, `security`, `hardware`, `power`, `desktop`, `virtualization`,
`database`, `maintenance`, `other`.

`profiles.json` contains the `office`, `developer`, and `minimum` profiles.
Every service referenced by a profile, label, or safe-to-disable list must
exist in `services.json`. The complete definitions are in [`schemas/`](schemas/).

English service descriptions are original technical summaries based on systemd
unit behavior and public systemd documentation. They are not copied from a
third-party application.

## Usage

```bash
curl -fsSL \
  https://raw.githubusercontent.com/06ergin06/systemd-service-db/main/data/services.json \
  -o services.json
```

```python
import json, urllib.request

URL = "https://raw.githubusercontent.com/06ergin06/systemd-service-db/main/data/services.json"
with urllib.request.urlopen(URL) as response:
    services = json.load(response)

print(services["cups.service"]["description_en"])
```

A pinned Git submodule is also supported. For production, pin a commit or tag.

## Validate

```bash
python3 scripts/validate.py
python3 scripts/validate.py --check-sorted
python3 scripts/validate.py --fix-sort
```

Checks JSON syntax, schemas, duplicate entries, references, flag consistency,
ASCII object keys, and sort order. It uses only the Python standard library.
CI runs the same checks on every push and pull request.

## Contribute

1. Add the service to `data/services.json`.
2. Provide both languages, choose a category, and set exactly one
   classification boolean.
3. Update `data/profiles.json` if profile behavior changes.
4. Run `python3 scripts/validate.py --fix-sort`.
5. Open a PR with the validation output.

Use English field names, profile identifiers, and category values. Localized
description and suggestion values are welcome.

## Sync

On `main` pushes touching `data/**`, GitHub Actions builds the compatibility
layout expected by the existing applications and pushes it to:

| Repository | Branch | Services | Profiles |
|---|---|---|---|
| `06ergin06/pardus-boot-analyzer` | `main` | `src/services_data.json` | `src/profiles_data.json` |
| `06ergin06/linux_boot_analyzer_tui` | `master` | `assets/services_data.json` | `assets/profiles_data.json` |

The adapter is isolated in `scripts/export_legacy.py`; the canonical data in
this repository remains English-identified. The workflow uses the `SYNC_PAT`
secret and the `systemd-service-db-bot` identity.

## License

MIT. This is an independent project. All contents of this repository are
provided under the MIT License only. See [`LICENSE`](LICENSE).
