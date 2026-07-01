#!/usr/bin/env python3
"""Run Publisher validation checks."""

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
    [sys.executable, "tools/check_verification_receipt_template.py"],
    [sys.executable, "tools/check_generate_papers_workflow.py"],
    [sys.executable, "tools/check_publisher_mirror_handoff.py"],
    [sys.executable, "tools/check_mirror_ecosystem_management_handoff.py"],
    [sys.executable, "tools/check_publisher_closure_evidence_production.py"],
    [sys.executable, "tools/check_publisher_self_managed_completion.py"],
    [sys.executable, "tools/check_governed_ecosystem_site_mirror_awareness.py"],
    [sys.executable, "tools/check_stegguardian_propagation_status.py"],
    [sys.executable, "tools/check_publisher_governed_ecosystem_sync_status.py"],
    [sys.executable, "tools/check_publisher_governed_ecosystem_validation_status.py"],
]


def main() -> int:
    for command in COMMANDS:
        completed = subprocess.run(command, cwd=REPO_ROOT)
        if completed.returncode != 0:
            return completed.returncode
    print("valid: Publisher checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
