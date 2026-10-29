#!/usr/bin/env python3
"""Export the legacy compatibility layout consumed by the existing apps.

The canonical files in this repository use English identifiers only.  The
existing GTK and TUI applications still expect the older field names and
profile identifiers, so the sync workflow calls this adapter instead of copying
the canonical files directly.  The adapter is intentionally isolated from the
data files and from the validator.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


def _legacy_service(record: dict[str, Any]) -> dict[str, Any]:
    if record.get("critical"):
        classification = "kritik"
    elif record.get("required"):
        classification = "gerekli"
    else:
        classification = "suggestion"

    return {
        "desc": record["description_tr"],
        "desc_en": record["description_en"],
        "suggestion": record["suggestion_tr"],
        "oneri_en": record["suggestion_en"],
        "tip": classification,
    }


def _legacy_profiles(data: dict[str, Any]) -> dict[str, Any]:
    profile_ids = {
        "office": "ofis",
        "developer": "yazilimci",
        "minimum": "minimum",
    }
    profile_keys = {
        "office": ("prof_office_name", "prof_office_desc"),
        "developer": ("prof_dev_name", "prof_dev_desc"),
        "minimum": ("prof_min_name", "prof_min_desc"),
    }
    profile_labels = {
        "bluetooth.service": "bluetooth_desc",
        "cups-browsed.service": "cups_browsed_desc",
        "cups.service": "cups_service_desc",
        "docker.service": "docker_desc",
        "mysql.service": "mysql_desc",
        "postgresql.service": "postgresql_desc",
        "ssh.service": "ssh_desc",
    }

    profiles: dict[str, Any] = {}
    for profile_id, profile in data["profiles"].items():
        legacy_id = profile_ids[profile_id]
        name_key, desc_key = profile_keys[profile_id]
        profiles[legacy_id] = {
            "name_tr_key": name_key,
            "desc_tr_key": desc_key,
            "icon": profile["icon"],
            "services": profile["services"],
        }

    return {
        "profiles": profiles,
        "safe_to_disable_services": data["safe_to_disable_services"],
        "profile_service_labels": profile_labels,
    }


def write_exports(services_out: Path, profiles_out: Path) -> None:
    services = json.loads((ROOT / "data" / "services.json").read_text(encoding="utf-8"))
    profiles = json.loads((ROOT / "data" / "profiles.json").read_text(encoding="utf-8"))

    legacy_services = {
        name: _legacy_service(record) for name, record in services.items()
    }
    legacy_profiles = _legacy_profiles(profiles)

    services_out.parent.mkdir(parents=True, exist_ok=True)
    profiles_out.parent.mkdir(parents=True, exist_ok=True)
    services_out.write_text(
        json.dumps(legacy_services, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    profiles_out.write_text(
        json.dumps(legacy_profiles, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--services-out",
        type=Path,
        required=True,
        help="destination for the legacy services file",
    )
    parser.add_argument(
        "--profiles-out",
        type=Path,
        required=True,
        help="destination for the legacy profiles file",
    )
    args = parser.parse_args()
    write_exports(args.services_out, args.profiles_out)
    print(f"wrote legacy exports to {args.services_out} and {args.profiles_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
