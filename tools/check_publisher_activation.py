#!/usr/bin/env python3
"""Run the complete Publisher local activation validation sequence."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    [sys.executable, "tools/check_emergency_ai_templates.py"],
    [sys.executable, "tools/validate_emergency_ai_cases.py"],
    [sys.executable, "tools/check_site_mirror_dispatch.py"],
    [sys.executable, "tools/check_release_gate.py"],
]


def main() -> int:
    for command in COMMANDS:
        print(f"running: {' '.join(command)}")
        completed = subprocess.run(command, cwd=REPO_ROOT)
        if completed.returncode != 0:
            print(f"activation validation failed: {' '.join(command)}")
            return completed.returncode

    print("valid: Publisher activation checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
