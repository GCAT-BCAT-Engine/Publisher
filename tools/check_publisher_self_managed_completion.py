#!/usr/bin/env python3
"""Validate Publisher self-managed completion status."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

CHECKS = {
    "docs/PUBLISHER_SELF_MANAGED_COMPLETION.md": [
        "repo_build_state: self_managed_completion_ready",
        "activation_state: pending_fresh_ordered_artifacts",
        "Publisher dispatch workflow emits non-activating verification receipt artifacts.",
        "Publisher closure updater updates docs/PUBLISHER_PENDING_CLOSURE_STATUS.md during unresolved attempts.",
        "This document is not an activation receipt.",
        "actual_fresh_publisher_receipt_artifact: required",
        "actual_fresh_site_evidence_artifact: required",
        "automated_closure_receipt_commit: required",
        "thread_archive_ready: true",
    ],
    "docs/PUBLISHER_MIRROR_HANDOFF.md": [
        "dispatch receipt posture env values",
        "verification receipt boundary",
        "Pending: actual Publisher receipt artifact, actual Site evidence artifact, and closure commit from the automated closure workflow.",
    ],
    "docs/MIRROR_ECOSYSTEM_MANAGEMENT_HANDOFF.md": [
        "self_managed_handoff_completion",
        "live GitHub Actions artifact production",
        "Publisher verification receipts preserve closure_evidence_results without claiming activation",
    ],
    "tools/close_site_mirror_activation.py": [
        "PENDING_STATUS_PATH",
        "write_pending_status",
        "write_closure_receipt",
    ],
    "tools/check_publisher_closure_evidence_production.py": [
        "PENDING_STATUS_PATH",
        "write_pending_status",
        "CLOSURE_EVIDENCE_STATUS: \"pending_fresh_ordered_artifacts\"",
    ],
}


def main() -> int:
    for rel_path, terms in CHECKS.items():
        path = ROOT / rel_path
        if not path.exists():
            print(f"publisher self-managed completion check failed: missing {rel_path}", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8")
        missing = [term for term in terms if term not in text]
        if missing:
            print(f"publisher self-managed completion check failed: {rel_path}", file=sys.stderr)
            for term in missing:
                print(f"missing: {term}", file=sys.stderr)
            return 1

    print("valid: publisher self-managed completion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
