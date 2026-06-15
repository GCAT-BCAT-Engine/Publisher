#!/usr/bin/env python3
"""Validate emergency AI restriction case objects."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


SCHEMA_PATH = Path("governance/schemas/emergency-ai-restriction.case.schema.json")
CASE_GLOB = "*.case.json"
CASE_DIR = Path("governance/cases")


def main() -> int:
    if not SCHEMA_PATH.exists():
        print(f"Missing schema: {SCHEMA_PATH}")
        return 1

    case_paths = sorted(CASE_DIR.glob(CASE_GLOB))
    if not case_paths:
        print("No emergency AI case JSON files found.")
        return 1

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    failures: list[str] = []
    for case_path in case_paths:
        data = json.loads(case_path.read_text(encoding="utf-8"))
        errors = sorted(validator.iter_errors(data), key=lambda error: list(error.path))
        if errors:
            for error in errors:
                location = ".".join(str(part) for part in error.path) or "<root>"
                failures.append(f"{case_path}: {location}: {error.message}")
        else:
            print(f"valid: {case_path}")

    if failures:
        print("\n".join(failures))
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
