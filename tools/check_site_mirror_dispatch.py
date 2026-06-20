#!/usr/bin/env python3
"""Verify Publisher-to-Site mirror dispatch and closure configuration."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    Path(".github/workflows/dispatch-site-mirror.yml"),
    Path(".github/workflows/close-site-mirror-activation.yml"),
    Path("docs/site-mirror-dispatch-protocol.md"),
    Path("docs/site-paper-display-policy.md"),
    Path("docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md"),
    Path("tools/write_verification_run_receipt.py"),
    Path("tools/close_site_mirror_activation.py"),
    Path("tools/check_publisher_closure_evidence_production.py"),
    Path("README.md"),
]

REQUIRED_WORKFLOW_TERMS = [
    "name: Dispatch Site Paper Mirror",
    "default: \"StegVerse-Labs/Site\"",
    "DEFAULT_SITE_REPOSITORY: \"StegVerse-Labs/Site\"",
    "DEFAULT_SOURCE_REPOSITORY: \"GCAT-BCAT-Engine/Publisher\"",
    "DEFAULT_SOURCE_REF: \"main\"",
    "SITE_MIRROR_DISPATCH_TOKEN",
    "dry_run",
    "Dry run requested. Publisher validation and dispatch configuration checks passed.",
    "python tools/check_publisher_activation.py",
    "actions/workflows/mirror-papers.yml/dispatches",
    "source_repository",
    "source_ref",
    "python tools/write_verification_run_receipt.py",
    "actions/upload-artifact@v4",
    "publisher-site-verification-receipt",
    "verification-runs/*.json",
]

REQUIRED_CLOSURE_WORKFLOW_TERMS = [
    "name: Close Site Mirror Activation",
    "docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md",
    "tools/check_publisher_closure_evidence_production.py",
    "python tools/check_publisher_closure_evidence_production.py",
    "python tools/close_site_mirror_activation.py",
    "docs/mirror-activation-closures",
    "Close activation from Publisher and Site evidence artifacts",
    "No activation closure changes to commit. Evidence may still be pending.",
]

REQUIRED_RECEIPT_WRITER_TERMS = [
    "receipt_type",
    "publisher_to_site_verification_run",
    "github_run_url",
    "site_dispatch_attempted",
    "dispatch_request_accepted",
    "pending_site_workflow_evidence",
]

REQUIRED_CLOSURE_SCRIPT_TERMS = [
    "PUBLISHER_ARTIFACT_PREFIX",
    "SITE_ARTIFACT_PREFIX",
    "publisher-site-verification-receipt",
    "site-mirror-evidence",
    "close_site_mirror_activation.py",
    "activation_state",
    "activated",
    "mirror-activation-closures",
]

REQUIRED_PROTOCOL_TERMS = [
    ".github/workflows/dispatch-site-mirror.yml",
    "Dispatch Site Paper Mirror",
    "python tools/check_publisher_activation.py",
    "docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md",
    "tools/check_publisher_closure_evidence_production.py",
    "Publisher activation validation passes",
    "StegVerse-Labs/Site/.github/workflows/mirror-papers.yml",
    "Mirror Papers from Publisher",
    "source_repository: GCAT-BCAT-Engine/Publisher",
    "source_ref: main",
    "SITE_MIRROR_DISPATCH_TOKEN",
    "STEGVERSE_REPO_SYNC_TOKEN",
    "Publisher closure writes a pending probe or activation closure receipt",
]

REQUIRED_CLOSURE_EVIDENCE_TERMS = [
    "Goal: Publisher closure evidence production",
    "publisher_artifact_prefix: publisher-site-verification-receipt",
    "site_artifact_prefix: site-mirror-evidence",
    "This pending probe is not an activation receipt.",
]

REQUIRED_README_TERMS = [
    "docs/site-mirror-dispatch-protocol.md",
    "SITE_MIRROR_DISPATCH_TOKEN",
    "github/workflows/dispatch-site-mirror.yml",
]


def fail(message: str) -> int:
    print(f"site mirror dispatch check failed: {message}")
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

    result = require_terms(Path(".github/workflows/dispatch-site-mirror.yml"), REQUIRED_WORKFLOW_TERMS)
    if result is not None:
        return result

    result = require_terms(Path(".github/workflows/close-site-mirror-activation.yml"), REQUIRED_CLOSURE_WORKFLOW_TERMS)
    if result is not None:
        return result

    result = require_terms(Path("tools/write_verification_run_receipt.py"), REQUIRED_RECEIPT_WRITER_TERMS)
    if result is not None:
        return result

    result = require_terms(Path("tools/close_site_mirror_activation.py"), REQUIRED_CLOSURE_SCRIPT_TERMS)
    if result is not None:
        return result

    result = require_terms(Path("docs/site-mirror-dispatch-protocol.md"), REQUIRED_PROTOCOL_TERMS)
    if result is not None:
        return result

    result = require_terms(Path("docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md"), REQUIRED_CLOSURE_EVIDENCE_TERMS)
    if result is not None:
        return result

    result = require_terms(Path("README.md"), REQUIRED_README_TERMS)
    if result is not None:
        return result

    print("valid: Publisher Site mirror dispatch and closure")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
