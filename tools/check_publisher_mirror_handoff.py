#!/usr/bin/env python3
"""Verify the current Publisher mirror handoff source of truth."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "PUBLISHER_MIRROR_HANDOFF.md"

REQUIRED_TERMS = [
    "# Publisher Mirror Handoff",
    "This file is the current handoff and task source of truth",
    "Standing-Proof-Engine v0.5.0 status",
    "StegVerse-Labs/Site",
    "StegVerse-Labs/Standing-Proof-Engine",
    "SPE_MIRROR_HANDOFF.md",
    "docs/release_snapshot_v0_5_0.md",
    "samples/destination_receipt_chain_001.json",
    "master-records/core-lite",
    "records/spe_destination_receipt_chain_001.json",
    "data/spe-v0-5-0-status.json",
    "StegVerse-Labs/admissibility-wiki",
    "StegVerse-002/stegguardian-wiki",
    "Wiki propagation verification",
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
    print("valid: current root Publisher mirror handoff")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
