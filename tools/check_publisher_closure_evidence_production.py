#!/usr/bin/env python3
"""Validate the Publisher closure evidence production packet."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "packet": ROOT / "docs" / "PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md",
    "workflow": ROOT / ".github" / "workflows" / "close-site-mirror-activation.yml",
    "dispatch_workflow": ROOT / ".github" / "workflows" / "dispatch-site-mirror.yml",
    "management_handoff": ROOT / "docs" / "MIRROR_ECOSYSTEM_MANAGEMENT_HANDOFF.md",
    "publisher_handoff": ROOT / "docs" / "PUBLISHER_MIRROR_HANDOFF.md",
    "activation_status": ROOT / "docs" / "activation-status.md",
    "pending_status": ROOT / "docs" / "PUBLISHER_PENDING_CLOSURE_STATUS.md",
    "pending_probe": ROOT / "docs" / "mirror-activation-closures" / "publisher-site-mirror-pending.json",
    "closure_script": ROOT / "tools" / "close_site_mirror_activation.py",
}

REQUIRED = {
    "packet": [
        "Goal: Publisher closure evidence production",
        "Repository: GCAT-BCAT-Engine/Publisher",
        "Target repository: StegVerse-Labs/Site",
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
        "Publisher closure evidence production is done",
        "Archive Readiness",
    ],
    "workflow": [
        "docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md",
        "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
        "tools/check_publisher_closure_evidence_production.py",
        "python tools/check_publisher_closure_evidence_production.py",
        "python tools/close_site_mirror_activation.py",
        "MAX_ARTIFACT_AGE_HOURS",
    ],
    "dispatch_workflow": [
        "docs/PUBLISHER_MIRROR_HANDOFF.md",
        "docs/MIRROR_ECOSYSTEM_MANAGEMENT_HANDOFF.md",
        "docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md",
        "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
        "tools/check_publisher_mirror_handoff.py",
        "tools/check_mirror_ecosystem_management_handoff.py",
        "tools/check_publisher_closure_evidence_production.py",
    ],
    "management_handoff": [
        "docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md",
        "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
        "StegVerse-Labs/Site/docs/TRANSITION_DISCOVERY_STATUS.md",
        "StegVerse-Labs/Site/data/transition-discovery-status-v1.json",
        "Publisher closure evidence production",
        "ready_for_fresh_ordered_automated_closure",
        "live GitHub Actions artifact production",
    ],
    "publisher_handoff": [
        "docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md",
        "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
        "Publisher closure evidence production",
        "actual Publisher receipt artifact",
        "actual Site evidence artifact",
        "pending-status boundary",
        "fresh ordered artifacts",
    ],
    "activation_status": [
        "ready_for_fresh_ordered_automated_closure",
        "actual fresh Publisher verification receipt artifact has not been recorded",
        "actual fresh Site evidence artifact has not been recorded",
        "Dispatch workflow watches Publisher continuation handoffs and pending closure status",
        "docs/PUBLISHER_PENDING_CLOSURE_STATUS.md",
        "Let the automated workflows proceed",
    ],
    "pending_status": [
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
        "valid: publisher closure evidence production",
    ],
    "pending_probe": [
        "pending_evidence",
        "This pending probe is not an activation receipt.",
        "publisher-site-verification-receipt",
        "site-mirror-evidence",
    ],
    "closure_script": [
        "PUBLISHER_ARTIFACT_PREFIX = \"publisher-site-verification-receipt\"",
        "SITE_ARTIFACT_PREFIX = \"site-mirror-evidence\"",
        "ORDER_GRACE_MINUTES = 5",
        "MAX_ARTIFACT_AGE_HOURS",
        "write_pending_probe",
        "write_closure_receipt",
    ],
}

FORBIDDEN = {
    "packet": [
        "Activation state: activated",
        "Activation: complete",
        "activation complete",
    ],
    "activation_status": [
        "activation_state: activated",
    ],
    "pending_status": [
        "closure_recorded_here: true",
        "publisher_receipt_recorded_here: true",
        "site_evidence_recorded_here: true",
    ],
}


def _read(label: str) -> str:
    path = FILES[label]
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def main() -> int:
    for label, terms in REQUIRED.items():
        try:
            text = _read(label)
        except FileNotFoundError as exc:
            print(f"publisher closure evidence production check failed: missing {exc.filename}", file=sys.stderr)
            return 1

        missing = [term for term in terms if term not in text]
        blocked = [term for term in FORBIDDEN.get(label, []) if term in text]
        if missing or blocked:
            print(f"publisher closure evidence production check failed: {label}", file=sys.stderr)
            for term in missing:
                print(f"missing: {term}", file=sys.stderr)
            for term in blocked:
                print(f"forbidden: {term}", file=sys.stderr)
            return 1

    print("valid: publisher closure evidence production")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
