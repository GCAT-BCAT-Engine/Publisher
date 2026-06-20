#!/usr/bin/env python3
"""Verify Publisher-to-Site verification receipt template fields."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = REPO_ROOT / "docs" / "verification-run-receipt.template.json"

REQUIRED_TOP_LEVEL_FIELDS = [
    "receipt_type",
    "status",
    "run_class",
    "publisher_repository",
    "site_repository",
    "publisher_workflow",
    "publisher_activation_runner",
    "site_workflow",
    "source_repository",
    "source_ref",
    "dry_run",
    "github_run_url",
    "github_run_id",
    "github_run_attempt",
    "observed_at_utc",
    "observed_by",
    "validation_results",
    "dispatch_results",
    "release_gate_results",
    "closure_evidence_results",
    "notes",
]

REQUIRED_VALIDATION_FIELDS = [
    "check_publisher_activation",
    "check_emergency_ai_templates",
    "validate_emergency_ai_cases",
    "check_site_mirror_dispatch",
    "check_release_gate",
    "check_verification_receipt_template",
    "check_generate_papers_workflow",
    "check_publisher_mirror_handoff",
    "check_mirror_ecosystem_management_handoff",
    "check_publisher_closure_evidence_production",
]

REQUIRED_DISPATCH_FIELDS = [
    "site_dispatch_attempted",
    "site_dispatch_status",
    "site_workflow_run_url",
    "site_commit_sha",
]

REQUIRED_RELEASE_GATE_FIELDS = [
    "publisher_source_validity",
    "dispatch_readiness",
    "site_mirror_validity",
    "public_display_verification",
    "governance_case_display_verification",
    "closure_evidence_verification",
]

REQUIRED_CLOSURE_EVIDENCE_FIELDS = [
    "publisher_artifact_prefix",
    "site_artifact_prefix",
    "publisher_verification_receipt_artifact",
    "site_evidence_artifact",
    "max_artifact_age_hours",
    "order_grace_minutes",
    "pending_probe_path",
    "closure_receipt_path",
    "closure_evidence_status",
    "non_claim",
]

EXPECTED_VALUES = {
    "receipt_type": "publisher_to_site_verification_run",
    "run_class": "dry_run_or_live_dispatch",
    "publisher_repository": "GCAT-BCAT-Engine/Publisher",
    "site_repository": "StegVerse-Labs/Site",
    "publisher_workflow": ".github/workflows/dispatch-site-mirror.yml",
    "publisher_activation_runner": "tools/check_publisher_activation.py",
    "site_workflow": "StegVerse-Labs/Site/.github/workflows/mirror-papers.yml",
    "source_repository": "GCAT-BCAT-Engine/Publisher",
    "source_ref": "main",
}

EXPECTED_CLOSURE_VALUES = {
    "publisher_artifact_prefix": "publisher-site-verification-receipt",
    "site_artifact_prefix": "site-mirror-evidence",
    "max_artifact_age_hours": 48,
    "order_grace_minutes": 5,
    "pending_probe_path": "docs/mirror-activation-closures/publisher-site-mirror-pending.json",
    "closure_evidence_status": "pending_fresh_ordered_artifacts",
}


def fail(message: str) -> int:
    print(f"verification receipt template check failed: {message}")
    return 1


def require_fields(mapping: dict, fields: list[str], label: str) -> int | None:
    for field in fields:
        if field not in mapping:
            return fail(f"missing {field!r} in {label}")
    return None


def main() -> int:
    if not RECEIPT_PATH.exists():
        return fail(f"missing required file: {RECEIPT_PATH.relative_to(REPO_ROOT)}")

    try:
        receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return fail(f"invalid JSON: {exc}")

    result = require_fields(receipt, REQUIRED_TOP_LEVEL_FIELDS, "receipt template")
    if result is not None:
        return result

    for field, expected in EXPECTED_VALUES.items():
        if receipt.get(field) != expected:
            return fail(f"expected {field!r} to be {expected!r}")

    result = require_fields(receipt["validation_results"], REQUIRED_VALIDATION_FIELDS, "validation_results")
    if result is not None:
        return result

    result = require_fields(receipt["dispatch_results"], REQUIRED_DISPATCH_FIELDS, "dispatch_results")
    if result is not None:
        return result

    result = require_fields(receipt["release_gate_results"], REQUIRED_RELEASE_GATE_FIELDS, "release_gate_results")
    if result is not None:
        return result

    closure_evidence = receipt["closure_evidence_results"]
    result = require_fields(closure_evidence, REQUIRED_CLOSURE_EVIDENCE_FIELDS, "closure_evidence_results")
    if result is not None:
        return result

    for field, expected in EXPECTED_CLOSURE_VALUES.items():
        if closure_evidence.get(field) != expected:
            return fail(f"expected closure_evidence_results.{field!r} to be {expected!r}")

    if "not an activation receipt" not in closure_evidence.get("non_claim", ""):
        return fail("closure_evidence_results.non_claim must preserve non-activation language")

    print("valid: Publisher verification receipt template")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
