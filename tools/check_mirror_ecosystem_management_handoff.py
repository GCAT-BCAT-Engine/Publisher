#!/usr/bin/env python3
"""Verify Publisher-to-Site mirror ecosystem management handoff."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    Path("docs/MIRROR_ECOSYSTEM_MANAGEMENT_HANDOFF.md"),
    Path("docs/PUBLISHER_MIRROR_HANDOFF.md"),
    Path("docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md"),
    Path("docs/PUBLISHER_PENDING_CLOSURE_STATUS.md"),
    Path("docs/verification-run-receipt.template.json"),
    Path("docs/activation-status.md"),
    Path("docs/verification-tracker.md"),
    Path("tools/close_site_mirror_activation.py"),
    Path("tools/write_verification_run_receipt.py"),
    Path("tools/check_verification_receipt_template.py"),
    Path("tools/check_publisher_closure_evidence_production.py"),
    Path(".github/workflows/dispatch-site-mirror.yml"),
    Path(".github/workflows/close-site-mirror-activation.yml"),
]

MANAGEMENT_TERMS = [
    "self_managed_handoff_ready",
    "self_managed_handoff_completion",
    "current_goal: Publisher closure evidence production",
    "docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md",
    "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
    "docs/verification-run-receipt.template.json",
    "tools/write_verification_run_receipt.py",
    "tools/check_verification_receipt_template.py",
    "StegVerse-Labs/Site/docs/TRANSITION_DISCOVERY_STATUS.md",
    "StegVerse-Labs/Site/data/transition-discovery-status-v1.json",
    "tools/check_publisher_closure_evidence_production.py",
    "thread_archive_ready: true",
    "automation chain",
    "acceptance criteria",
    "live GitHub Actions artifact production",
    "the pending closure status is not an activation receipt",
    "Publisher verification receipts preserve closure_evidence_results without claiming activation",
    "fresh, ordered, and evidence-valid",
]

PUBLISHER_HANDOFF_TERMS = [
    "Goal: Publisher closure evidence production",
    "docs/MIRROR_ECOSYSTEM_MANAGEMENT_HANDOFF.md",
    "docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md",
    "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
    "tools/check_publisher_closure_evidence_production.py",
    "docs/verification-run-receipt.template.json",
    "tools/check_verification_receipt_template.py",
    "tools/write_verification_run_receipt.py",
    "closure_evidence_results",
    "closure_evidence_verification",
    "not activation receipts",
    "self_managed_handoff_completion",
    "fresh ordered artifacts",
]

CLOSURE_EVIDENCE_TERMS = [
    "Goal: Publisher closure evidence production",
    "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
    "Publisher state: ready_for_fresh_ordered_automated_closure",
    "Site state: repository_managed_continuation_complete",
    "Activation state: pending_fresh_ordered_artifacts",
    "publisher-site-verification-receipt",
    "site-mirror-evidence",
    "This pending probe is not an activation receipt.",
]

PENDING_STATUS_TERMS = [
    "Publisher Pending Closure Status",
    "status: waiting_for_fresh_ordered_artifact_pair",
    "publisher_prefix: publisher-site-verification-receipt",
    "site_prefix: site-mirror-evidence",
    "publisher_receipt_recorded_here: false",
    "site_evidence_recorded_here: false",
    "closure_recorded_here: false",
    "pending_probe_only: true",
    "valid: publisher closure evidence production",
]

RECEIPT_TEMPLATE_TERMS = [
    "closure_evidence_results",
    "closure_evidence_verification",
    "publisher-site-verification-receipt",
    "site-mirror-evidence",
    "pending_fresh_ordered_artifacts",
    "This receipt is not an activation receipt until a closure receipt is written.",
]

STATUS_TERMS = [
    "ready_for_fresh_ordered_automated_closure",
    "Publisher closure evidence production packet exists",
    "Publisher pending closure status exists",
    "Publisher closure workflow checks Publisher closure evidence production before closure attempt",
    "Publisher closure workflow watches Publisher pending closure status",
    "Publisher closure script rejects stale or out-of-order Publisher/Site artifact pairs",
    "MAX_ARTIFACT_AGE_HOURS",
    "ORDER_GRACE_MINUTES",
]

CLOSURE_SCRIPT_TERMS = [
    "artifact_freshness_ready",
    "write_pending_probe",
    "write_closure_receipt",
    "update_tracker",
    "update_status",
]


def fail(message: str) -> int:
    print(f"mirror ecosystem management handoff check failed: {message}")
    return 1


def read(path: Path) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def require_file(path: Path) -> int | None:
    if not (REPO_ROOT / path).exists():
        return fail(f"missing required file: {path}")
    return None


def require_terms(path: Path, terms: list[str]) -> int | None:
    text = read(path)
    normalized_text = text.casefold()
    for term in terms:
        if term.casefold() not in normalized_text:
            return fail(f"missing {term!r} in {path}")
    return None


def main() -> int:
    for path in REQUIRED_FILES:
        result = require_file(path)
        if result is not None:
            return result

    checks = [
        (Path("docs/MIRROR_ECOSYSTEM_MANAGEMENT_HANDOFF.md"), MANAGEMENT_TERMS),
        (Path("docs/PUBLISHER_MIRROR_HANDOFF.md"), PUBLISHER_HANDOFF_TERMS),
        (Path("docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md"), CLOSURE_EVIDENCE_TERMS),
        (Path("docs/PUBLISHER_PENDING_CLOSURE_STATUS.md"), PENDING_STATUS_TERMS),
        (Path("docs/verification-run-receipt.template.json"), RECEIPT_TEMPLATE_TERMS),
        (Path("docs/activation-status.md"), STATUS_TERMS),
        (Path("tools/close_site_mirror_activation.py"), CLOSURE_SCRIPT_TERMS),
    ]
    for path, terms in checks:
        result = require_terms(path, terms)
        if result is not None:
            return result

    print("valid: mirror ecosystem management handoff")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
