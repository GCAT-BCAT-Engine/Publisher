#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_TRUE = (
    "authoritative_vs_effective_database_distinguished",
    "unknown_retention_preserved",
    "external_ai_returns_non_authoritative",
    "publication_projection_grants_no_authority",
)


def main() -> int:
    if len(sys.argv) != 2:
        return 2
    receipt = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    failures: list[str] = []
    if receipt.get("destination") != "GCAT-BCAT-Engine/Publisher":
        failures.append("wrong destination")
    checks = receipt.get("checks", {})
    for key in REQUIRED_TRUE:
        if checks.get(key) is not True:
            failures.append(f"required check failed: {key}")
    for key, value in receipt.get("authority", {}).items():
        if value is not False:
            failures.append(f"authority must remain false: {key}")
    decision = receipt.get("decision")
    if decision == "PASS" and checks.get("site_downstream_ingestion_packet_verified") is not True:
        failures.append("PASS requires verified Site downstream-ingestion packet")
    if decision not in {"PASS", "BLOCK"}:
        failures.append("decision must be PASS or BLOCK")
    if failures:
        for failure in failures:
            print(f"BLOCK: {failure}")
        return 1
    print(f"VALID: Publisher verification decision {decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
