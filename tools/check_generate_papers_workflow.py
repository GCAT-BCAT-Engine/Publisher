#!/usr/bin/env python3
"""Verify Generate Papers JSON workflow uses Publisher root paths."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = REPO_ROOT / ".github/workflows/generate-papers.yml"

REQUIRED_TERMS = [
    "name: Generate Papers JSON",
    "papers_manifest.yml",
    "with open('papers_manifest.yml')",
    "with open('papers.json', 'w')",
    "git add papers.json",
    "permissions:",
    "contents: write",
]

FORBIDDEN_TERMS = [
    "publisher/papers_manifest.yml",
    "publisher/papers.json",
]


def fail(message: str) -> int:
    print(f"generate papers workflow check failed: {message}")
    return 1


def main() -> int:
    if not WORKFLOW_PATH.exists():
        return fail("missing .github/workflows/generate-papers.yml")

    text = WORKFLOW_PATH.read_text(encoding="utf-8")

    for term in REQUIRED_TERMS:
        if term not in text:
            return fail(f"missing required term: {term}")

    for term in FORBIDDEN_TERMS:
        if term in text:
            return fail(f"forbidden nested Publisher path remains: {term}")

    print("valid: Generate Papers JSON workflow")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
