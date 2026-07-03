#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = [
    [sys.executable, "scripts/check_repo_standards_import_awareness.py"],
    [sys.executable, "scripts/check_publisher_workflow.py"],
    [sys.executable, "scripts/check_publisher_repo_local_complete.py"],
]


def main() -> int:
    for command in COMMANDS:
        result = subprocess.run(command, cwd=ROOT, text=True)
        if result.returncode != 0:
            print("PUBLISHER READINESS: FAIL")
            return result.returncode
    print("PUBLISHER READINESS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
