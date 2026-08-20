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
    if HANDOFF.exists():
        handoff_text = HANDOFF.read_text(encoding="utf-8")
        # Validate durable semantics instead of coupling CI to a prose heading.
        # The canonical handoff may be reorganized without invalidating adoption
        # as long as the active ST-017 goal and installed validation surfaces remain.
        for marker in [
            "goal_id: PUBLISHER-ST017-SITE-PROPAGATION-001",
            "tools/run_sandbox_validation.py",
            "templates/sandbox-first/publisher.sandbox-profile.json",
            "tools/check_st017_sandbox_report.py",
            "tools/check_publisher_st017_activation.py",
            "tools/check_st017_sandbox_adoption.py",
            ".github/workflows/validate-governed-ecosystem-awareness.yml",
        ]:
            if marker not in handoff_text:
                errors.append(f"handoff_missing:{marker}")
    if errors:
        print("PUBLISHER ST-017 ADOPTION: FAIL - " + ", ".join(errors))
        return 1
    print("PUBLISHER ST-017 ADOPTION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
