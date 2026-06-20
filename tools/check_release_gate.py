#!/usr/bin/env python3
"""Verify Publisher-to-Site release gate documentation and workflow hooks."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    Path("docs/release-gate-checklist.md"),
    Path("docs/site-mirror-dispatch-protocol.md"),
    Path("docs/site-paper-display-policy.md"),
    Path("docs/validation.md"),
    Path("docs/verification-tracker.md"),
    Path("docs/iphone-dry-run-runbook.md"),
    Path("docs/verification-run-receipt.template.json"),
    Path("docs/PUBLISHER_PENDING_CLOSURE_STATUS.md"),
    Path("docs/PUBLISHER_SELF_MANAGED_COMPLETION.md"),
    Path("docs/activation-status.md"),
    Path("docs/PUBLISHER_MIRROR_HANDOFF.md"),
    Path("docs/MIRROR_ECOSYSTEM_MANAGEMENT_HANDOFF.md"),
    Path("docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md"),
    Path(".github/workflows/dispatch-site-mirror.yml"),
    Path(".github/workflows/close-site-mirror-activation.yml"),
    Path(".github/workflows/validate-emergency-ai-cases.yml"),
    Path("tools/check_site_mirror_dispatch.py"),
    Path("tools/check_publisher_activation.py"),
    Path("tools/check_publisher_mirror_handoff.py"),
    Path("tools/check_mirror_ecosystem_management_handoff.py"),
    Path("tools/check_publisher_self_managed_completion.py"),
    Path("tools/check_verification_receipt_template.py"),
    Path("tools/write_verification_run_receipt.py"),
    Path("tools/check_publisher_closure_evidence_production.py"),
    Path("README.md"),
]

CHECKS = {
    Path("docs/release-gate-checklist.md"): [
        "Gate 6 — Closure Evidence Verification",
        "python tools/check_publisher_activation.py",
        "python tools/check_verification_receipt_template.py",
        "python tools/check_publisher_closure_evidence_production.py",
        "Publisher verification receipt artifact exists",
        "Publisher verification receipt preserves closure_evidence_results",
        "Publisher verification receipt preserves closure_evidence_verification",
        "Publisher verification receipts are not activation receipts.",
        "Site evidence artifact exists",
        "MAX_ARTIFACT_AGE_HOURS",
        "ORDER_GRACE_MINUTES",
        "Publisher pending closure status remains waiting_for_fresh_ordered_artifact_pair until closure",
        "The pending closure status is not an activation receipt.",
        "The pending probe is not an activation receipt.",
    ],
    Path("docs/site-mirror-dispatch-protocol.md"): [
        "docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md",
        "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
        "publisher_receipt_recorded_here: false",
        "site_evidence_recorded_here: false",
        "closure_recorded_here: false",
        "pending_probe_only: true",
    ],
    Path("docs/validation.md"): [
        "Closure Workflow Validation",
        "python tools/check_publisher_mirror_handoff.py",
        "python tools/check_mirror_ecosystem_management_handoff.py",
        "python tools/check_publisher_closure_evidence_production.py",
        "python tools/check_publisher_self_managed_completion.py",
        "python tools/close_site_mirror_activation.py",
        "docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md",
        "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
        "close-workflow self-managed completion check drifts",
        "valid: Publisher activation checks",
        "valid: Publisher to Site release gate",
        "valid: publisher closure evidence production",
        "valid: publisher self-managed completion",
        "Publisher closure evidence production drifts",
    ],
    Path("tools/check_publisher_activation.py"): [
        "tools/check_site_mirror_dispatch.py",
        "tools/check_release_gate.py",
        "tools/check_publisher_mirror_handoff.py",
        "tools/check_mirror_ecosystem_management_handoff.py",
        "tools/check_publisher_closure_evidence_production.py",
        "tools/check_publisher_self_managed_completion.py",
        "valid: Publisher activation checks",
    ],
    Path("docs/verification-tracker.md"): [
        "status: pending_fresh_ordered_artifacts",
        "activation_boundary: Publisher closure evidence production",
        "publisher-site-verification-receipt-<run>-<attempt>",
        "site-mirror-evidence-<run>-<attempt>",
        "MAX_ARTIFACT_AGE_HOURS: 48",
        "ORDER_GRACE_MINUTES: 5",
        "tools/check_publisher_closure_evidence_production.py",
        "publisher_activation_closure_receipt: PENDING",
        "The pending probe is not an activation receipt.",
    ],
    Path("docs/iphone-dry-run-runbook.md"): [
        "iPhone Dry-Run Runbook",
        "Actions → Dispatch Site Paper Mirror",
        "dry_run: true",
        "valid: Publisher activation checks",
    ],
    Path("docs/verification-run-receipt.template.json"): [
        "publisher_to_site_verification_run",
        "dry_run_or_live_dispatch",
        "GCAT-BCAT-Engine/Publisher",
        "StegVerse-Labs/Site",
        "github_run_url",
        "site_dispatch_attempted",
        "closure_evidence_results",
        "closure_evidence_verification",
        "publisher-site-verification-receipt",
        "site-mirror-evidence",
        "This receipt is not an activation receipt until a closure receipt is written.",
    ],
    Path("docs/PUBLISHER_PENDING_CLOSURE_STATUS.md"): [
        "Publisher Pending Closure Status",
        "status: waiting_for_fresh_ordered_artifact_pair",
        "publisher_prefix: publisher-site-verification-receipt",
        "site_prefix: site-mirror-evidence",
        "publisher_receipt_recorded_here: false",
        "site_evidence_recorded_here: false",
        "closure_recorded_here: false",
        "pending_probe_only: true",
    ],
    Path("docs/PUBLISHER_SELF_MANAGED_COMPLETION.md"): [
        "repo_build_state: self_managed_completion_ready",
        "activation_state: pending_fresh_ordered_artifacts",
        "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
        "The pending closure status is not an activation receipt.",
        "thread_archive_ready: true",
    ],
    Path("docs/activation-status.md"): [
        "activation_state: ready_for_fresh_ordered_automated_closure",
        "repo_build_state: self_managed_completion_ready",
        "Activation runner validates Publisher closure evidence production packet",
        "Activation runner validates Publisher self-managed completion",
        "Publisher closure evidence production packet exists",
        "Publisher pending closure status exists",
        "Publisher self-managed completion status exists",
        "Validation workflow watches Publisher handoffs, closure packet, pending status, and self-managed completion",
        "Publisher closure workflow checks Publisher closure evidence production before closure attempt",
        "Publisher closure workflow checks Publisher self-managed completion before closure attempt",
        "docs/PUBLISHER_SELF_MANAGED_COMPLETION.md",
        "tools/check_publisher_self_managed_completion.py",
        "actual fresh Publisher verification receipt artifact has not been recorded",
        "actual fresh Site evidence artifact has not been recorded",
        "automated closure receipt has not been generated",
    ],
    Path("README.md"): [
        "docs/release-gate-checklist.md",
        "docs/activation-status.md",
        "docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md",
        "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
        "The pending closure status is not activation evidence.",
        "closure evidence verification",
        "Publisher receipt artifact",
        "Site evidence artifact",
        "closure receipt",
        "python tools/check_publisher_activation.py",
        "python tools/check_publisher_closure_evidence_production.py",
    ],
    Path(".github/workflows/dispatch-site-mirror.yml"): [
        "python tools/check_publisher_activation.py",
        "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
        "tools/check_publisher_closure_evidence_production.py",
        "Dry run requested. Publisher validation and dispatch configuration checks passed.",
        "Site mirror dispatch was not attempted.",
    ],
    Path(".github/workflows/close-site-mirror-activation.yml"): [
        "python tools/check_publisher_closure_evidence_production.py",
        "python tools/check_publisher_self_managed_completion.py",
        "python tools/close_site_mirror_activation.py",
        "docs/PUBLISHER_SELF_MANAGED_COMPLETION.md",
    ],
    Path(".github/workflows/validate-emergency-ai-cases.yml"): [
        "python tools/check_publisher_activation.py",
        "tools/check_publisher_mirror_handoff.py",
        "tools/check_mirror_ecosystem_management_handoff.py",
        "tools/check_publisher_closure_evidence_production.py",
        "tools/check_publisher_self_managed_completion.py",
        "docs/PUBLISHER_MIRROR_HANDOFF.md",
        "docs/MIRROR_ECOSYSTEM_MANAGEMENT_HANDOFF.md",
        "docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md",
        "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
        "docs/PUBLISHER_SELF_MANAGED_COMPLETION.md",
        ".github/workflows/close-site-mirror-activation.yml",
    ],
    Path("docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md"): [
        "Goal: Publisher closure evidence production",
        "Activation state: pending_fresh_ordered_artifacts",
        "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
        "publisher_artifact_prefix: publisher-site-verification-receipt",
        "site_artifact_prefix: site-mirror-evidence",
        "This pending probe is not an activation receipt.",
    ],
}


def fail(message: str) -> int:
    print(f"release gate check failed: {message}")
    return 1


def read(path: Path) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def require_file(path: Path) -> int | None:
    if not (REPO_ROOT / path).exists():
        return fail(f"missing required file: {path}")
    return None


def require_terms(path: Path, terms: list[str]) -> int | None:
    text = read(path)
    for term in terms:
        if term not in text:
            return fail(f"missing {term!r} in {path}")
    return None


def main() -> int:
    for path in REQUIRED_FILES:
        result = require_file(path)
        if result is not None:
            return result

    for path, terms in CHECKS.items():
        result = require_terms(path, terms)
        if result is not None:
            return result

    print("valid: Publisher to Site release gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
