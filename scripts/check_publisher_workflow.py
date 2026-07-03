#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT / ".github" / "workflows" / "publisher-check.yml"
READINESS = ROOT / ".github" / "workflows" / "publisher-readiness.yml"


def require(path: Path, snippets: list[str]) -> None:
    if not path.exists():
        raise SystemExit(f"PUBLISHER WORKFLOW: FAIL - missing {path.relative_to(ROOT)}")
    text = path.read_text(encoding="utf-8")
    missing = [item for item in snippets if item not in text]
    if missing:
        raise SystemExit(f"PUBLISHER WORKFLOW: FAIL - required text missing in {path.relative_to(ROOT)}")


def main() -> int:
    require(PRIMARY, [
        "name: Publisher Check",
        "pull_request:",
        "push:",
        "workflow_dispatch:",
        "python scripts/check_repo_standards_import_awareness.py",
    ])
    require(READINESS, [
        "name: Publisher Readiness",
        "pull_request:",
        "push:",
        "workflow_dispatch:",
        "python scripts/check_publisher_readiness.py",
    ])
    print("PUBLISHER WORKFLOW: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
