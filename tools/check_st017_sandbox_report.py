#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "reports" / "sandbox-first-validation.report.json"
DEFAULT_STATE = ROOT / "reports" / "st017-task-state.json"
REQUIRED_COMMAND_IDS = {
    "compile-python",
    "validate-governed-awareness",
    "validate-publisher-activation",
    "validate-st017-adoption",
}
VALID_STATES = {"COMPLETE", "BLOCKED", "RETRY", "REVIEW_REQUIRED", "FAILED"}


def canonical_hash(data: Any) -> str:
    payload = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("report_root_not_object")
    return value


def evaluate(report: dict[str, Any]) -> tuple[str, list[str]]:
    errors: list[str] = []
    if report.get("record_type") != "sandbox_validation_report":
        errors.append("record_type_invalid")
    if report.get("repository") != "GCAT-BCAT-Engine/Publisher":
        errors.append("repository_mismatch")
    if report.get("profile_id") != "publisher-governed-awareness":
        errors.append("profile_id_mismatch")
    if report.get("sandbox_status") != "PASS":
        errors.append("sandbox_not_pass")

    results = report.get("results")
    if not isinstance(results, list):
        errors.append("results_not_list")
        results = []

    seen: set[str] = set()
    for result in results:
        if not isinstance(result, dict):
            errors.append("result_not_object")
            continue
        command_id = result.get("id")
        if not isinstance(command_id, str):
            errors.append("result_id_missing")
            continue
        if command_id in seen:
            errors.append(f"duplicate_result:{command_id}")
        seen.add(command_id)
        if result.get("passed") is not True:
            errors.append(f"command_failed:{command_id}")
        if result.get("timed_out") is True:
            errors.append(f"command_timed_out:{command_id}")

    for command_id in sorted(REQUIRED_COMMAND_IDS - seen):
        errors.append(f"required_result_missing:{command_id}")
    for command_id in sorted(seen - REQUIRED_COMMAND_IDS):
        errors.append(f"unexpected_result:{command_id}")

    non_claims = report.get("non_claims")
    if not isinstance(non_claims, dict):
        errors.append("non_claims_missing")
    else:
        for key in ("release_authority", "publication_authority", "downstream_authority", "admissibility"):
            if non_claims.get(key) is not False:
                errors.append(f"non_claim_not_false:{key}")

    return ("COMPLETE" if not errors else "FAILED"), errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--state-output", type=Path, default=DEFAULT_STATE)
    args = parser.parse_args()

    state = "FAILED"
    errors: list[str] = []
    report_hash = None
    try:
        if not args.report.exists():
            raise FileNotFoundError("report_missing")
        report = load_json(args.report)
        report_hash = canonical_hash(report)
        state, errors = evaluate(report)
    except Exception as exc:  # fail closed and persist the reason
        errors = [f"report_unreadable:{type(exc).__name__}:{exc}"]

    if state not in VALID_STATES:
        state = "FAILED"
        errors.append("invalid_internal_state")

    output = {
        "schema_version": "1.0.0",
        "record_type": "st017_task_state",
        "repository": "GCAT-BCAT-Engine/Publisher",
        "owner": "GCAT-BCAT-Engine/Publisher:.github/workflows/validate-governed-ecosystem-awareness.yml",
        "trigger": "pull_request|push|schedule|workflow_dispatch",
        "state": state,
        "report_path": args.report.as_posix(),
        "report_sha256": report_hash,
        "errors": errors,
        "next_executable_task": (
            "validate-job" if state == "COMPLETE" else "repair-first-failing-sandbox-command"
        ),
        "duplicate_execution_key": report_hash,
        "release_condition": "state==COMPLETE",
        "authority": {
            "publication": False,
            "release": False,
            "activation": False,
            "admissibility": False,
        },
    }
    args.state_output.parent.mkdir(parents=True, exist_ok=True)
    args.state_output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PUBLISHER ST-017 REPORT STATE: {state}")
    for error in errors:
        print(f"- {error}")
    return 0 if state == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
