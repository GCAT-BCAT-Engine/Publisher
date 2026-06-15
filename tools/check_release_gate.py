#!/usr/bin/env python3
"""Verify Publisher-to-Site release gate documentation and workflow hooks."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    Path("docs/release-gate-checklist.md"),
    Path("docs/site-mirror-dispatch-protocol.md"),
    Path("docs/site-paper-display-policy.md"),
    Path("docs/verification-tracker.md"),
    Path(".github/workflows/dispatch-site-mirror.yml"),
    Path("tools/check_site_mirror_dispatch.py"),
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

REQUIRED_TRACKER_TERMS = [
    "status: pending_dry_run",
    "Run Dispatch Site Paper Mirror manually with dry_run: true",
    "Confirm tools/check_site_mirror_dispatch.py passes",
    "Confirm tools/check_release_gate.py passes",
    "Install or confirm SITE_MIRROR_DISPATCH_TOKEN in Publisher",
    "Confirm Site policy checker runs before mirroring",
    "Confirm governance case posture is not strengthened by Site wording",
    "docs/release-gate-checklist.md",
]

REQUIRED_README_TERMS = [
    "docs/release-gate-checklist.md",
    "Publisher source validity",
    "dispatch readiness",
    "Site mirror validity",
    "public display verification",
    "governance case posture checks",
]

REQUIRED_WORKFLOW_TERMS = [
    "python tools/check_emergency_ai_templates.py",
    "python tools/validate_emergency_ai_cases.py",
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

    result = require_terms(Path("docs/verification-tracker.md"), REQUIRED_TRACKER_TERMS)
    if result is not None:
        return result

    result = require_terms(Path("README.md"), REQUIRED_README_TERMS)
    if result is not None:
        return result

    result = require_terms(Path(".github/workflows/dispatch-site-mirror.yml"), REQUIRED_WORKFLOW_TERMS)
    if result is not None:
        return result

    print("valid: Publisher to Site release gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
