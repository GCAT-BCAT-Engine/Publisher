#!/usr/bin/env python3
"""Run Publisher validation checks."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Full repository activation checks. These intentionally include dynamic handoff
# and release-readiness assertions and may fail while unrelated workstreams are
# incomplete.
COMMANDS = [
    [sys.executable, "tools/check_emergency_ai_templates.py"],
    [sys.executable, "tools/validate_emergency_ai_cases.py"],
    [sys.executable, "tools/check_site_mirror_dispatch.py"],
    [sys.executable, "tools/check_release_gate_compat.py"],
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

# ST-017 validates the bounded governed-awareness surface only. It must not be
# coupled to unrelated evolving publication, SPE, paper, or release workstreams.
ST017_COMMANDS = [
    [sys.executable, "tools/check_governed_ecosystem_site_mirror_awareness.py"],
    [sys.executable, "tools/check_stegguardian_propagation_status.py"],
    [sys.executable, "tools/check_publisher_governed_ecosystem_sync_status.py"],
    [sys.executable, "tools/check_publisher_governed_ecosystem_validation_status.py"],
    [sys.executable, "tools/check_publisher_governed_ecosystem_workflow_request.py"],
]


def run_commands(commands: list[list[str]]) -> int:
    for command in commands:
        completed = subprocess.run(command, cwd=REPO_ROOT)
        if completed.returncode != 0:
            return completed.returncode
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=("full", "st017"), default="full")
    args = parser.parse_args()

    commands = ST017_COMMANDS if args.scope == "st017" else COMMANDS
    result = run_commands(commands)
    if result != 0:
        return result
    print(f"valid: Publisher activation checks scope={args.scope}")
    print("valid: Publisher checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
