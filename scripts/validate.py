#!/usr/bin/env python3
"""Validate the systemd service database without third-party dependencies.

The validator intentionally implements the small JSON Schema subset used by
``schemas/service.schema.json`` and ``schemas/profile.schema.json``.  It also
performs cross-file checks that JSON Schema cannot express: key/name equality,
flag consistency, profile references, ASCII identifiers and sort order.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SERVICES_PATH = ROOT / "data" / "services.json"
PROFILES_PATH = ROOT / "data" / "profiles.json"
SERVICE_SCHEMA_PATH = ROOT / "schemas" / "service.schema.json"
PROFILE_SCHEMA_PATH = ROOT / "schemas" / "profile.schema.json"

SERVICE_NAME_RE = r"^[a-zA-Z0-9_\-\@\.]+\.service$"
FORBIDDEN_PROFILE_IDS = {"ofis", "yazilimci"}


class DataError(Exception):
    """Raised when a data file cannot be parsed or has an invalid shape."""


class DuplicateKeyError(DataError):
    def __init__(self, key: str) -> None:
        super().__init__(f"duplicate JSON key: {key!r}")
        self.key = key


def _json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(key)
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    if not path.is_file():
        raise DataError(f"missing file: {path}")
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text, object_pairs_hook=_json_pairs)
    except DuplicateKeyError:
        raise
    except json.JSONDecodeError as exc:
        raise DataError(
            f"{path}: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc


def _json_equal(left: Any, right: Any) -> bool:
    return json.dumps(left, sort_keys=True, ensure_ascii=False) == json.dumps(
        right, sort_keys=True, ensure_ascii=False
    )


class SchemaLite:
    """A deliberately small JSON Schema Draft 2020-12 validator."""

    def __init__(self, schema: dict[str, Any]) -> None:
        self.root = schema

    def validate(self, instance: Any, path: str = "$") -> list[str]:
        errors: list[str] = []
        self._validate(instance, self.root, path, errors)
        return errors

    def _resolve(self, ref: str) -> dict[str, Any]:
        if not ref.startswith("#/"):
            raise DataError(f"unsupported $ref: {ref!r}")
        node: Any = self.root
        for token in ref[2:].split("/"):
            token = token.replace("~1", "/").replace("~0", "~")
            node = node[token]
        return node

    @staticmethod
    def _is_type(instance: Any, expected: str) -> bool:
        if expected == "object":
            return isinstance(instance, dict)
        if expected == "array":
            return isinstance(instance, list)
        if expected == "string":
            return isinstance(instance, str)
        if expected == "boolean":
            return isinstance(instance, bool)
        if expected == "integer":
            return isinstance(instance, int) and not isinstance(instance, bool)
        if expected == "number":
            return isinstance(instance, (int, float)) and not isinstance(instance, bool)
        if expected == "null":
            return instance is None
        return False

    def _validate(
        self,
        instance: Any,
        schema: Any,
        path: str,
        errors: list[str],
    ) -> None:
        if len(errors) >= 200:
            return
        if schema is True:
            return
        if schema is False:
            errors.append(f"{path}: value is not allowed")
            return
        if not isinstance(schema, dict):
            return

        if "$ref" in schema:
            self._validate(instance, self._resolve(schema["$ref"]), path, errors)
            return

        expected_type = schema.get("type")
        if expected_type is not None:
            types = expected_type if isinstance(expected_type, list) else [expected_type]
            if not any(self._is_type(instance, item) for item in types):
                errors.append(
                    f"{path}: expected {' or '.join(types)}, got "
                    f"{type(instance).__name__}"
                )
                return

        if "const" in schema and not _json_equal(instance, schema["const"]):
            errors.append(f"{path}: expected constant {schema['const']!r}")

        if "enum" in schema:
            if not any(_json_equal(instance, option) for option in schema["enum"]):
                errors.append(
                    f"{path}: value {instance!r} is not one of {schema['enum']!r}"
                )

        if isinstance(instance, str):
            if "minLength" in schema and len(instance) < schema["minLength"]:
                errors.append(
                    f"{path}: string is shorter than {schema['minLength']} characters"
                )
            if "maxLength" in schema and len(instance) > schema["maxLength"]:
                errors.append(
                    f"{path}: string is longer than {schema['maxLength']} characters"
                )
            if "pattern" in schema:
                if re.search(schema["pattern"], instance) is None:
                    errors.append(
                        f"{path}: {instance!r} does not match {schema['pattern']!r}"
                    )

        if isinstance(instance, (int, float)) and not isinstance(instance, bool):
            if "minimum" in schema and instance < schema["minimum"]:
                errors.append(f"{path}: value is below minimum {schema['minimum']}")
            if "maximum" in schema and instance > schema["maximum"]:
                errors.append(f"{path}: value is above maximum {schema['maximum']}")

        if isinstance(instance, list):
            if "minItems" in schema and len(instance) < schema["minItems"]:
                errors.append(
                    f"{path}: array has fewer than {schema['minItems']} items"
                )
            if "maxItems" in schema and len(instance) > schema["maxItems"]:
                errors.append(
                    f"{path}: array has more than {schema['maxItems']} items"
                )
            if schema.get("uniqueItems"):
                seen: set[str] = set()
                for index, item in enumerate(instance):
                    marker = json.dumps(item, sort_keys=True, ensure_ascii=False)
                    if marker in seen:
                        errors.append(f"{path}[{index}]: duplicate item")
                    seen.add(marker)
            item_schema = schema.get("items")
            if item_schema is not None:
                for index, item in enumerate(instance):
                    self._validate(item, item_schema, f"{path}[{index}]", errors)

        if isinstance(instance, dict):
            if "minProperties" in schema and len(instance) < schema["minProperties"]:
                errors.append(
                    f"{path}: object has fewer than {schema['minProperties']} properties"
                )
            if "maxProperties" in schema and len(instance) > schema["maxProperties"]:
                errors.append(
                    f"{path}: object has more than {schema['maxProperties']} properties"
                )

            required = schema.get("required", [])
            for key in required:
                if key not in instance:
                    errors.append(f"{path}: missing required property {key!r}")

            properties = schema.get("properties", {})
            pattern_properties = schema.get("patternProperties", {})
            additional = schema.get("additionalProperties", True)
            matched: set[str] = set()

            for key, value in instance.items():
                if key in properties:
                    matched.add(key)
                    self._validate(value, properties[key], f"{path}.{key}", errors)
                for pattern, sub_schema in pattern_properties.items():
                    if re.search(pattern, key) is not None:
                        matched.add(key)
                        self._validate(value, sub_schema, f"{path}.{key}", errors)
                if key not in properties and key not in matched:
                    if additional is False:
                        errors.append(f"{path}: unexpected property {key!r}")
                    elif isinstance(additional, dict):
                        self._validate(value, additional, f"{path}.{key}", errors)

            property_names = schema.get("propertyNames")
            if property_names is not None:
                for key in instance:
                    self._validate(key, property_names, f"{path}.<key>", errors)

        for sub_schema in schema.get("allOf", []):
            self._validate(instance, sub_schema, path, errors)

        any_of = schema.get("anyOf")
        if any_of:
            if not any(not self._collect(instance, sub_schema) for sub_schema in any_of):
                errors.append(f"{path}: does not match any allowed variant")

        one_of = schema.get("oneOf")
        if one_of:
            matches = sum(
                1 for sub_schema in one_of if not self._collect(instance, sub_schema)
            )
            if matches != 1:
                errors.append(f"{path}: must match exactly one variant")

    def _collect(self, instance: Any, schema: Any) -> list[str]:
        errors: list[str] = []
        self._validate(instance, schema, "$", errors)
        return errors


def _check_sorted(services: dict[str, Any]) -> list[str]:
    names = list(services)
    ordered = sorted(names, key=lambda name: (name.casefold(), name))
    if names == ordered:
        return []
    for index, (actual, expected) in enumerate(zip(names, ordered)):
        if actual != expected:
            return [
                "services.json is not alphabetically sorted: "
                f"position {index} is {actual!r}, expected {expected!r}. "
                "Run: python3 scripts/validate.py --fix-sort"
            ]
    return ["services.json is not alphabetically sorted"]


def _check_services(services: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key, record in services.items():
        if not isinstance(record, dict):
            continue

        if record.get("name") != key:
            errors.append(
                f"$.{key}.name: expected {key!r}, got {record.get('name')!r}"
            )

        flags = (
            record.get("safe_to_disable"),
            record.get("critical"),
            record.get("required"),
        )
        if sum(value is True for value in flags) != 1:
            errors.append(
                f"$.{key}: exactly one of safe_to_disable, critical and required "
                f"must be true, got {flags}"
            )
    return errors


def _check_profiles(profiles_doc: dict[str, Any], services: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    profiles = profiles_doc.get("profiles", {})
    if not isinstance(profiles, dict):
        return ["$.profiles: expected an object"]

    for profile_id, profile in profiles.items():
        if not isinstance(profile, dict):
            continue
        if profile_id in FORBIDDEN_PROFILE_IDS:
            errors.append(
                f"$.profiles.{profile_id}: legacy Turkish profile identifiers "
                "are not allowed; use an English identifier"
            )
        if profile.get("id") != profile_id:
            errors.append(
                f"$.profiles.{profile_id}.id: expected {profile_id!r}, "
                f"got {profile.get('id')!r}"
            )
        rules = profile.get("services", {})
        if isinstance(rules, dict):
            for service_name in rules:
                if service_name not in services:
                    errors.append(
                        f"$.profiles.{profile_id}.services.{service_name}: "
                        "service is not defined in data/services.json"
                    )

    safe_services = profiles_doc.get("safe_to_disable_services", [])
    if isinstance(safe_services, list):
        for service_name in safe_services:
            record = services.get(service_name)
            if record is None:
                errors.append(
                    f"$.safe_to_disable_services: {service_name!r} is not defined "
                    "in data/services.json"
                )
            elif not record.get("safe_to_disable"):
                errors.append(
                    f"$.safe_to_disable_services: {service_name!r} is not marked "
                    "safe_to_disable"
                )

    labels = profiles_doc.get("labels", {})
    if isinstance(labels, dict):
        for service_name in labels:
            if service_name not in services:
                errors.append(
                    f"$.labels.{service_name}: service is not defined in "
                    "data/services.json"
                )

    return errors


def _check_ascii_keys(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str) or not key.isascii():
                errors.append(f"{path}: non-ASCII object key {key!r}")
            errors.extend(_check_ascii_keys(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_check_ascii_keys(child, f"{path}[{index}]"))
    return errors


def _sort_services_file(path: Path) -> bool:
    data = load_json(path)
    if not isinstance(data, dict):
        raise DataError(f"{path}: expected a JSON object at the top level")
    ordered = dict(sorted(data.items(), key=lambda item: (item[0].casefold(), item[0])))
    if list(ordered) == list(data):
        print("services.json is already sorted.")
        return False
    path.write_text(
        json.dumps(ordered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("Sorted services.json.")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-sorted",
        action="store_true",
        help="require services.json keys to be alphabetically sorted (the default)",
    )
    parser.add_argument(
        "--fix-sort",
        action="store_true",
        help="rewrite services.json with alphabetically sorted keys, then validate",
    )
    args = parser.parse_args(argv)

    errors: list[str] = []
    try:
        if args.fix_sort:
            _sort_services_file(SERVICES_PATH)

        services = load_json(SERVICES_PATH)
        profiles_doc = load_json(PROFILES_PATH)
        service_schema = load_json(SERVICE_SCHEMA_PATH)
        profile_schema = load_json(PROFILE_SCHEMA_PATH)
    except DataError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not isinstance(services, dict):
        errors.append("data/services.json: expected a JSON object at the top level")
    else:
        errors.extend(SchemaLite(service_schema).validate(services))
        errors.extend(_check_services(services))
        errors.extend(_check_ascii_keys(services))
        # Sorting is always checked; --check-sorted is kept as an explicit CI
        # switch so the intent is visible in the workflow file.
        errors.extend(_check_sorted(services))

    if not isinstance(profiles_doc, dict):
        errors.append("data/profiles.json: expected a JSON object at the top level")
    else:
        errors.extend(SchemaLite(profile_schema).validate(profiles_doc))
        errors.extend(_check_ascii_keys(profiles_doc))
        if isinstance(services, dict):
            errors.extend(_check_profiles(profiles_doc, services))

    if errors:
        print(f"{len(errors)} validation error(s):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    assert isinstance(services, dict)
    profiles = profiles_doc.get("profiles", {}) if isinstance(profiles_doc, dict) else {}
    print(
        f"OK: {len(services)} services, {len(profiles)} profiles; "
        "JSON syntax, schema, references, flags and sort order are valid."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
