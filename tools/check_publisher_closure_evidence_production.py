#!/usr/bin/env python3
"""Validate Publisher closure evidence production files."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

CHECKS = {
    "docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md": [
        "Goal: Publisher closure evidence production",
        "Publisher state: ready_for_fresh_ordered_automated_closure",
        "Site state: repository_managed_continuation_complete",
        "Activation state: pending_fresh_ordered_artifacts",
        "publisher-site-verification-receipt",
        "site-mirror-evidence",
        "MAX_ARTIFACT_AGE_HOURS: 48",
        "ORDER_GRACE_MINUTES: 5",
        "This pending probe is not an activation receipt.",
        "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
        "docs/mirror-activation-closures/publisher-site-mirror-pending.json",
        "docs/mirror-activation-closures/publisher-site-mirror-closure-<timestamp>.json",
    ],
    ".github/workflows/close-site-mirror-activation.yml": [
        "docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md",
        "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
        "python tools/check_publisher_closure_evidence_production.py",
        "python tools/close_site_mirror_activation.py",
        "MAX_ARTIFACT_AGE_HOURS",
        "ORDER_GRACE_MINUTES",
    ],
    ".github/workflows/dispatch-site-mirror.yml": [
        "docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md",
        "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
        "CLOSURE_EVIDENCE_STATUS: \"pending_fresh_ordered_artifacts\"",
        "CLOSURE_EVIDENCE_VERIFICATION: \"pending_fresh_ordered_artifacts\"",
    ],
    "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md": [
        "Publisher Pending Closure Status",
        "status: waiting_for_fresh_ordered_artifact_pair",
        "publisher_prefix: publisher-site-verification-receipt",
        "site_prefix: site-mirror-evidence",
        "max_age_hours: 48",
        "order_grace_minutes: 5",
        "publisher_receipt_recorded_here: false",
        "site_evidence_recorded_here: false",
        "closure_recorded_here: false",
        "pending_probe_only: true",
    ],
    "tools/close_site_mirror_activation.py": [
        "PUBLISHER_ARTIFACT_PREFIX = \"publisher-site-verification-receipt\"",
        "SITE_ARTIFACT_PREFIX = \"site-mirror-evidence\"",
        "ORDER_GRACE_MINUTES = 5",
        "PENDING_STATUS_PATH",
        "write_pending_status",
        "write_pending_probe",
        "write_closure_receipt",
    ],
    "docs/PUBLISHER_MIRROR_HANDOFF.md": [
        "Publisher closure evidence production",
        "pending-status boundary",
        "Verification Receipt Boundary",
        "dispatch receipt posture env values",
    ],
    "docs/MIRROR_ECOSYSTEM_MANAGEMENT_HANDOFF.md": [
        "Publisher closure evidence production",
        "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
        "Publisher verification receipts preserve closure_evidence_results without claiming activation",
    ],
}


def main() -> int:
    for rel_path, terms in CHECKS.items():
        path = ROOT / rel_path
        if not path.exists():
            print(f"publisher closure evidence production check failed: missing {rel_path}", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8")
        missing = [term for term in terms if term not in text]
        if missing:
            print(f"publisher closure evidence production check failed: {rel_path}", file=sys.stderr)
            for term in missing:
                print(f"missing: {term}", file=sys.stderr)
            return 1

    print("valid: publisher closure evidence production")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
