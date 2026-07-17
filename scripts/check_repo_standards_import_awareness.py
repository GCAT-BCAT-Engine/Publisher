#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "repo-standards-import-awareness.md"
STATUS = ROOT / "data" / "repo-standards-import-awareness.json"
HANDOFF = ROOT / "PUBLISHER_MIRROR_HANDOFF.md"


def read(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"REPO STANDARDS IMPORT AWARENESS: FAIL - missing {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def main() -> int:
    doc = read(DOC)
    handoff = read(HANDOFF)
    data = json.loads(read(STATUS))

    if "READY_FOR_UPSTREAM_GATE_EVENTS" not in doc:
        raise SystemExit("REPO STANDARDS IMPORT AWARENESS: FAIL - doc status missing")

    # The active handoff may evolve to a newer repository goal, but it must
    # preserve the earlier Standing-Proof Engine boundary rather than delete it.
    spe_markers = ("Standing-Proof-Engine v0.5.0", "Standing-Proof Engine", "SPE v0.5.0")
    if not any(marker in handoff for marker in spe_markers):
        raise SystemExit("REPO STANDARDS IMPORT AWARENESS: FAIL - Standing-Proof Engine continuity not preserved")

    if "This file is the current handoff and task source of truth" not in handoff:
        raise SystemExit("REPO STANDARDS IMPORT AWARENESS: FAIL - active handoff source-of-truth declaration missing")

    expected = {
        "status_id": "repo-standards-import-awareness",
        "repository": "GCAT-BCAT-Engine/Publisher",
        "status": "READY_FOR_UPSTREAM_GATE_EVENTS",
        "next_action": "WAIT_FOR_UPSTREAM_GATE_EVENTS",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            raise SystemExit(f"REPO STANDARDS IMPORT AWARENESS: FAIL - {key} expected {value!r}, got {data.get(key)!r}")
    print("REPO STANDARDS IMPORT AWARENESS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
