#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "publisher-check.yml"


def main() -> int:
    if not WORKFLOW.exists():
        raise SystemExit("PUBLISHER WORKFLOW: FAIL - workflow missing")
    text = WORKFLOW.read_text(encoding="utf-8")
    required = [
        "name: Publisher Check",
        "pull_request:",
        "push:",
        "workflow_dispatch:",
        "python scripts/check_repo_standards_import_awareness.py",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise SystemExit("PUBLISHER WORKFLOW: FAIL - required workflow text missing")
    print("PUBLISHER WORKFLOW: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
