#!/usr/bin/env python3
"""Validate only the bounded Publisher ST-017 governed-awareness surface."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = [
    [sys.executable, "tools/check_governed_ecosystem_site_mirror_awareness.py"],
    [sys.executable, "tools/check_stegguardian_propagation_status.py"],
    [sys.executable, "tools/check_publisher_governed_ecosystem_sync_status.py"],
    [sys.executable, "tools/check_publisher_governed_ecosystem_validation_status.py"],
    [sys.executable, "tools/check_publisher_governed_ecosystem_workflow_request.py"],
]


def main() -> int:
    for command in COMMANDS:
        completed = subprocess.run(command, cwd=ROOT)
        if completed.returncode != 0:
            return completed.returncode
    print("valid: Publisher ST-017 governed-awareness activation boundary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
