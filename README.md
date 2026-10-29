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
.github/workflows/       # validate.yml, sync.yml
```

## Data

Each service in `data/services.json` has `name`, `description_tr/en`,
`suggestion_tr/en`, `category`, `safe_to_disable`, `critical`, `required`, plus
legacy mirrors (`desc`, `desc_en`, `suggestion`, `oneri_en`, `tip`). Legacy
fields must match the canonical fields exactly.

| `tip` | `safe_to_disable` | `critical` | `required` |
|---|---:|---:|---:|
| `suggestion` | `true` | `false` | `false` |
| `kritik` | `false` | `true` | `false` |
| `gerekli` | `false` | `false` | `true` |

Categories: `system`, `boot`, `network`, `bluetooth`, `printing`, `telemetry`,
`storage`, `security`, `hardware`, `power`, `desktop`, `virtualization`,
`database`, `maintenance`, `other`.

`profiles.json` stores profile metadata and `enable`/`disable` rules. Every
referenced service must exist in `services.json`. See [`schemas/`](schemas/)
for full definitions.

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

Checks JSON syntax, schemas, duplicates, references, flag consistency, and sort
order. Uses only the Python standard library. CI runs on every push and PR.

## Contribute

1. Add the service to `data/services.json`.
2. Provide both languages, choose a category, and keep legacy fields equal.
3. Update `data/profiles.json` if profile behavior changes.
4. Run `python3 scripts/validate.py --fix-sort`.
5. Open a PR with the validation output.

## Sync

On `main` pushes touching `data/**`, GitHub Actions copies the files to:

| Repository | Branch | Services | Profiles |
|---|---|---|---|
| `06ergin06/pardus-boot-analyzer` | `main` | `src/services_data.json` | `src/profiles_data.json` |
| `06ergin06/linux_boot_analyzer_tui` | `master` | `assets/services_data.json` | `assets/profiles_data.json` |

It uses the `SYNC_PAT` secret and the `systemd-service-db-bot` identity.

## License

MIT. Source projects are GPL-3.0; legal review is recommended before
redistribution. See [`LICENSE`](LICENSE).
