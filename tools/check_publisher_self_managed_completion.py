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
        "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
        "docs/PUBLISHER_VALIDATION_REMAINDER.md",
        "Issue #1 is not activation evidence.",
        "This document is not an activation receipt.",
        "The validation remainder document is not activation evidence.",
        "The pending closure status is not an activation receipt.",
        "actual_fresh_publisher_receipt_artifact: required",
        "actual_fresh_site_evidence_artifact: required",
        "automated_closure_receipt_commit: required",
        "thread_archive_ready: true",
    ],
    "docs/PUBLISHER_MIRROR_HANDOFF.md": [
        "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
        "docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md",
        "docs/PUBLISHER_VALIDATION_REMAINDER.md",
        "Issue #1 is not activation evidence.",
        "tools/check_publisher_closure_evidence_production.py",
        "self_managed_handoff_completion",
        "actual Publisher receipt artifact",
        "actual Site evidence artifact",
    ],
    "docs/MIRROR_ECOSYSTEM_MANAGEMENT_HANDOFF.md": [
        "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
        "classification: self_managed_handoff_completion",
        "thread_archive_ready: true",
        "pending closure status",
    ],
    "docs/PUBLISHER_VALIDATION_REMAINDER.md": [
        "repo_build_state: self_managed_completion_ready",
        "activation_state: pending_fresh_ordered_artifacts",
        "fresh Publisher verification receipt artifact: required",
        "fresh Site mirror evidence artifact: required",
        "This validation remainder is not an activation receipt.",
    ],
    "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md": [
        "Publisher Pending Closure Status",
        "status: waiting_for_fresh_ordered_artifact_pair",
        "publisher_receipt_recorded_here: false",
        "site_evidence_recorded_here: false",
        "closure_recorded_here: false",
        "pending_probe_only: true",
        "valid: publisher closure evidence production",
    ],
    "tools/close_site_mirror_activation.py": [
        "PENDING_STATUS_PATH",
        "write_pending_status",
        "write_pending_probe",
        "write_closure_receipt",
    ],
    "tools/check_publisher_closure_evidence_production.py": [
        "pending_status",
        "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
        "publisher_receipt_recorded_here: false",
        "site_evidence_recorded_here: false",
        "closure_recorded_here: false",
    ],
    ".github/workflows/dispatch-site-mirror.yml": [
        "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
        "tools/check_publisher_closure_evidence_production.py",
    ],
    ".github/workflows/close-site-mirror-activation.yml": [
        "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
        "tools/check_publisher_closure_evidence_production.py",
        "python tools/close_site_mirror_activation.py",
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
