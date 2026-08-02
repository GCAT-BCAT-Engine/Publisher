#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "templates/sandbox-first/publisher.sandbox-profile.json"
RUNNER = ROOT / "tools/run_sandbox_validation.py"
REPORT_VALIDATOR = ROOT / "tools/check_st017_sandbox_report.py"
WORKFLOW = ROOT / ".github/workflows/validate-governed-ecosystem-awareness.yml"
HANDOFF = ROOT / "docs/PUBLISHER_MIRROR_HANDOFF.md"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--structural-only", action="store_true")
    parser.parse_args()
    errors = []
    for path in [PROFILE, RUNNER, REPORT_VALIDATOR, WORKFLOW, HANDOFF]:
        if not path.exists():
            errors.append(f"missing:{path.relative_to(ROOT)}")
    if PROFILE.exists():
        data = json.loads(PROFILE.read_text(encoding="utf-8"))
        if data.get("repository") != "GCAT-BCAT-Engine/Publisher":
            errors.append("profile_repository_mismatch")
        ids = [item.get("id") for item in data.get("commands", [])]
        for required in ["compile-python", "validate-governed-awareness", "validate-publisher-activation", "validate-st017-adoption"]:
            if required not in ids:
                errors.append(f"profile_missing:{required}")
    if WORKFLOW.exists():
        text = WORKFLOW.read_text(encoding="utf-8")
        for marker in [
            "pull_request:",
            "python tools/run_sandbox_validation.py",
            "python tools/check_st017_sandbox_report.py",
            "publisher-st017-sandbox-report",
            "reports/sandbox-first-validation.report.json",
            "reports/st017-task-state.json",
        ]:
            if marker not in text:
                errors.append(f"workflow_missing:{marker}")
    if REPORT_VALIDATOR.exists():
        validator_text = REPORT_VALIDATOR.read_text(encoding="utf-8")
        for marker in ["COMPLETE", "FAILED", "duplicate_execution_key", "next_executable_task"]:
            if marker not in validator_text:
                errors.append(f"report_validator_missing:{marker}")
    if HANDOFF.exists() and "ST-017 Sandbox-First Adoption" not in HANDOFF.read_text(encoding="utf-8"):
        errors.append("handoff_missing_st017")
    if errors:
        print("PUBLISHER ST-017 ADOPTION: FAIL - " + ", ".join(errors))
        return 1
    print("PUBLISHER ST-017 ADOPTION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
