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
    Path("docs/activation-status.md"),
    Path(".github/workflows/dispatch-site-mirror.yml"),
    Path(".github/workflows/validate-emergency-ai-cases.yml"),
    Path("tools/check_site_mirror_dispatch.py"),
    Path("tools/check_publisher_activation.py"),
    Path("README.md"),
]

REQUIRED_CHECKLIST_TERMS = [
    "A green workflow alone is not the full release gate",
    "Gate 1 — Publisher Source Validity",
    "Gate 2 — Dispatch Readiness",
    "Gate 3 — Site Mirror Validity",
    "Gate 4 — Public Display Verification",
    "Gate 5 — Governance Case Display Verification",
    "python tools/check_emergency_ai_templates.py",
    "python tools/validate_emergency_ai_cases.py",
    "python tools/check_site_mirror_dispatch.py",
    "dry_run: true has passed",
    "SITE_MIRROR_DISPATCH_TOKEN is installed in Publisher for live dispatch",
    "Site policy checker runs before mirroring",
    "Site display does not overwrite Publisher status or posture",
    "Site text does not convert disputed or provisional claims into final findings",
]

REQUIRED_VALIDATION_DOC_TERMS = [
    "Publisher-to-Site activation also requires release-gate validation",
    "tools/check_site_mirror_dispatch.py",
    "tools/check_release_gate.py",
    "tools/check_publisher_activation.py",
    "docs/release-gate-checklist.md",
    "docs/verification-tracker.md",
    "docs/iphone-dry-run-runbook.md",
    "docs/verification-run-receipt.template.json",
    "docs/activation-status.md",
    "github/workflows/dispatch-site-mirror.yml",
    "python tools/check_publisher_activation.py",
    "python tools/check_site_mirror_dispatch.py",
    "python tools/check_release_gate.py",
    "valid: Publisher activation checks",
    "valid: Publisher Site mirror dispatch",
    "valid: Publisher to Site release gate",
    "release-gate documentation drifts",
    "verification receipt template drifts",
    "activation status drifts",
]

REQUIRED_ACTIVATION_RUNNER_TERMS = [
    "Run the complete Publisher local activation validation sequence",
    "tools/check_emergency_ai_templates.py",
    "tools/validate_emergency_ai_cases.py",
    "tools/check_site_mirror_dispatch.py",
    "tools/check_release_gate.py",
    "activation validation failed",
    "valid: Publisher activation checks",
]

REQUIRED_TRACKER_TERMS = [
    "status: pending_dry_run",
    "docs/iphone-dry-run-runbook.md",
    "docs/verification-run-receipt.template.json",
    "Run Dispatch Site Paper Mirror manually with dry_run: true",
    "Confirm tools/check_site_mirror_dispatch.py passes",
    "Confirm tools/check_release_gate.py passes",
    "Capture the dry-run result using docs/verification-run-receipt.template.json",
    "Install or confirm SITE_MIRROR_DISPATCH_TOKEN in Publisher",
    "Confirm Site policy checker runs before mirroring",
    "Confirm governance case posture is not strengthened by Site wording",
    "Capture the live-dispatch result using docs/verification-run-receipt.template.json",
    "docs/release-gate-checklist.md",
]

REQUIRED_IPHONE_RUNBOOK_TERMS = [
    "iPhone Dry-Run Runbook",
    "GitHub mobile app or Safari",
    "Actions → Dispatch Site Paper Mirror",
    "branch: main",
    "site_repository: StegVerse-Labs/Site",
    "source_ref: main",
    "dry_run: true",
    "Check emergency AI templates",
    "Validate emergency AI case objects",
    "Check Site mirror dispatch configuration",
    "Check Publisher to Site release gate",
    "Stop after validation for dry run",
    "Require dispatch token",
    "Dispatch Site mirror workflow",
    "Dry run requested. Publisher validation and dispatch configuration checks passed.",
    "Site mirror dispatch was not attempted.",
]

REQUIRED_RECEIPT_TERMS = [
    "publisher_to_site_verification_run",
    "dry_run_or_live_dispatch",
    "GCAT-BCAT-Engine/Publisher",
    "StegVerse-Labs/Site",
    ".github/workflows/dispatch-site-mirror.yml",
    "StegVerse-Labs/Site/.github/workflows/mirror-papers.yml",
    "github_run_url",
    "github_run_id",
    "check_emergency_ai_templates",
    "validate_emergency_ai_cases",
    "check_site_mirror_dispatch",
    "check_release_gate",
    "site_dispatch_attempted",
    "not_attempted_for_dry_run",
    "publisher_source_validity",
    "dispatch_readiness",
    "site_mirror_validity",
    "public_display_verification",
    "governance_case_display_verification",
]

REQUIRED_ACTIVATION_TERMS = [
    "activation_state: ready_for_manual_dry_run",
    "activation_target: Publisher to Site mirror dispatch",
    "site_target: StegVerse-Labs/Site",
    "manual dry-run has not been recorded",
    "SITE_MIRROR_DISPATCH_TOKEN has not been verified in Publisher",
    "Repo activation occurs when",
    "Dispatch Site Paper Mirror passes with dry_run: true",
    "Verification receipt is captured for the dry run",
    "Dispatch Site Paper Mirror passes with dry_run: false",
    "Site Mirror Papers from Publisher completes",
    "docs/verification-tracker.md is updated from pending_dry_run to activated",
]

REQUIRED_README_TERMS = [
    "docs/release-gate-checklist.md",
    "docs/activation-status.md",
    "Publisher source validity",
    "dispatch readiness",
    "Site mirror validity",
    "public display verification",
    "governance case posture checks",
    "manual dry-run execution",
    "dry-run receipt capture",
    "live dispatch",
    "Site mirror completion",
    "live-dispatch receipt capture",
    "verification tracker update to `activated`",
    "python tools/check_publisher_activation.py",
    "The activation runner executes",
    "python tools/check_site_mirror_dispatch.py",
    "python tools/check_release_gate.py",
    "docs/iphone-dry-run-runbook.md",
    "docs/verification-run-receipt.template.json",
]

REQUIRED_DISPATCH_WORKFLOW_TERMS = [
    "python tools/check_emergency_ai_templates.py",
    "python tools/validate_emergency_ai_cases.py",
    "python tools/check_site_mirror_dispatch.py",
    "python tools/check_release_gate.py",
]

REQUIRED_VALIDATION_WORKFLOW_TERMS = [
    "tools/check_site_mirror_dispatch.py",
    "tools/check_release_gate.py",
    "docs/release-gate-checklist.md",
    "docs/verification-tracker.md",
    "docs/iphone-dry-run-runbook.md",
    "docs/verification-run-receipt.template.json",
    "docs/activation-status.md",
    ".github/workflows/dispatch-site-mirror.yml",
    "python tools/check_site_mirror_dispatch.py",
    "python tools/check_release_gate.py",
]


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

    result = require_terms(Path("docs/release-gate-checklist.md"), REQUIRED_CHECKLIST_TERMS)
    if result is not None:
        return result

    result = require_terms(Path("docs/validation.md"), REQUIRED_VALIDATION_DOC_TERMS)
    if result is not None:
        return result

    result = require_terms(Path("tools/check_publisher_activation.py"), REQUIRED_ACTIVATION_RUNNER_TERMS)
    if result is not None:
        return result

    result = require_terms(Path("docs/verification-tracker.md"), REQUIRED_TRACKER_TERMS)
    if result is not None:
        return result

    result = require_terms(Path("docs/iphone-dry-run-runbook.md"), REQUIRED_IPHONE_RUNBOOK_TERMS)
    if result is not None:
        return result

    result = require_terms(Path("docs/verification-run-receipt.template.json"), REQUIRED_RECEIPT_TERMS)
    if result is not None:
        return result

    result = require_terms(Path("docs/activation-status.md"), REQUIRED_ACTIVATION_TERMS)
    if result is not None:
        return result

    result = require_terms(Path("README.md"), REQUIRED_README_TERMS)
    if result is not None:
        return result

    result = require_terms(Path(".github/workflows/dispatch-site-mirror.yml"), REQUIRED_DISPATCH_WORKFLOW_TERMS)
    if result is not None:
        return result

    result = require_terms(Path(".github/workflows/validate-emergency-ai-cases.yml"), REQUIRED_VALIDATION_WORKFLOW_TERMS)
    if result is not None:
        return result

    print("valid: Publisher to Site release gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
