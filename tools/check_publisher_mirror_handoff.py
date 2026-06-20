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
    "Publisher remains the source of truth",
    "Dispatch Site Paper Mirror",
    "Close Site Mirror Activation",
    "docs/MIRROR_ECOSYSTEM_MANAGEMENT_HANDOFF.md",
    "docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md",
    "python tools/check_publisher_activation.py",
    "tools/check_publisher_mirror_handoff.py",
    "tools/check_mirror_ecosystem_management_handoff.py",
    "tools/check_publisher_closure_evidence_production.py",
    "python tools/close_site_mirror_activation.py",
    "publisher-site-verification-receipt-<run>-<attempt>",
    "site-mirror-evidence-<run>-<attempt>",
    "docs/mirror-activation-closures/<closure>.json",
    "actual Publisher receipt artifact",
    "actual Site evidence artifact",
    "closure commit from the automated closure workflow",
    "Prior chat thread context is not required",
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
