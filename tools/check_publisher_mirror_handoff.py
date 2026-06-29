#!/usr/bin/env python3
"""Verify the Publisher mirror handoff document."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "docs" / "PUBLISHER_MIRROR_HANDOFF.md"

REQUIRED_TERMS = [
    "# Publisher Mirror Handoff",
    "Goal: Publisher closure evidence production",
    "GCAT-BCAT-Engine/Publisher",
    "StegVerse-Labs/Site",
    "pending_fresh_ordered_artifacts",
    "self_managed_handoff_completion",
    "docs/PUBLISHER_SELF_MANAGED_COMPLETION.md",
    "tools/check_publisher_self_managed_completion.py",
    "repo_build_state: self_managed_completion_ready",
    "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
    "docs/MIRROR_ECOSYSTEM_MANAGEMENT_HANDOFF.md",
    "docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md",
    "docs/PUBLISHER_VALIDATION_REMAINDER.md",
    "docs/SOURCE_GEOMETRY_PROVENANCE.md",
    "Source authority: StegVerse-Labs/admissibility-wiki",
    "Source authority page: docs/formalisms/original-drawing-reference.md",
    "Source Geometry ID: SG-001",
    "Creator: Rigel Randolph",
    "Classification: pre-BCAT/GCAT precursor source geometry",
    "Publisher role: citation and publication surface only",
    "Publisher must not become the custody authority, proof authority, priority authority, or derivation authority for the source geometry.",
    "The Source Geometry Provenance note is not custody authority or proof authority.",
    "Issue #1 is not activation evidence.",
    "Issue #1 records final closure-checker handoff-term alignment.",
    "actual Publisher receipt artifact",
    "actual Site evidence artifact",
    "closure commit from the automated closure workflow",
]


def main() -> int:
    if not HANDOFF.exists():
        print(f"missing handoff: {HANDOFF.relative_to(ROOT)}")
        return 1
    content = HANDOFF.read_text(encoding="utf-8")
    missing = [term for term in REQUIRED_TERMS if term not in content]
    if missing:
        print("publisher mirror handoff check failed")
        for term in missing:
            print(f"missing: {term}")
        return 1
    print("valid: publisher mirror handoff")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
