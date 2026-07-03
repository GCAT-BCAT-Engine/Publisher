#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "data" / "publisher-repo-local-complete.json"


def main() -> int:
    if not STATUS.exists():
        raise SystemExit("PUBLISHER LOCAL COMPLETE: FAIL - status missing")
    data = json.loads(STATUS.read_text(encoding="utf-8"))
    expected = {
        "status_id": "publisher-repo-local-complete",
        "repository": "GCAT-BCAT-Engine/Publisher",
        "repo_local_build": "AUTOMATED_VALIDATION_READY",
        "active_handoff": "PUBLISHER_MIRROR_HANDOFF.md",
        "validation_command": "python scripts/check_publisher_readiness.py",
        "next_action": "WAIT_FOR_UPSTREAM_GATE_EVENTS",
        "archive_status": "READY_FOR_HANDOFF",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            raise SystemExit(f"PUBLISHER LOCAL COMPLETE: FAIL - {key} expected {value!r}, got {data.get(key)!r}")
    surfaces = data.get("installed_surfaces")
    if not isinstance(surfaces, list) or "scripts/check_publisher_readiness.py" not in surfaces:
        raise SystemExit("PUBLISHER LOCAL COMPLETE: FAIL - readiness script not listed")
    print("PUBLISHER LOCAL COMPLETE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
