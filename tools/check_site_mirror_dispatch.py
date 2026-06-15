#!/usr/bin/env python3
"""Verify Publisher-to-Site mirror dispatch configuration."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    Path(".github/workflows/dispatch-site-mirror.yml"),
    Path("docs/site-mirror-dispatch-protocol.md"),
    Path("docs/site-paper-display-policy.md"),
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
    "python tools/check_emergency_ai_templates.py",
    "python tools/validate_emergency_ai_cases.py",
    "python tools/check_site_mirror_dispatch.py",
    "actions/workflows/mirror-papers.yml/dispatches",
    "source_repository",
    "source_ref",
]

REQUIRED_PROTOCOL_TERMS = [
    ".github/workflows/dispatch-site-mirror.yml",
    "Dispatch Site Paper Mirror",
    "StegVerse-Labs/Site/.github/workflows/mirror-papers.yml",
    "Mirror Papers from Publisher",
    "source_repository: GCAT-BCAT-Engine/Publisher",
    "source_ref: main",
    "SITE_MIRROR_DISPATCH_TOKEN",
    "STEGVERSE_REPO_SYNC_TOKEN",
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

    result = require_terms(Path("docs/site-mirror-dispatch-protocol.md"), REQUIRED_PROTOCOL_TERMS)
    if result is not None:
        return result

    result = require_terms(Path("README.md"), REQUIRED_README_TERMS)
    if result is not None:
        return result

    print("valid: Publisher Site mirror dispatch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
