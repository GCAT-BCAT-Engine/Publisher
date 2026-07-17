"""Governed admission for Continuity Vault recall exports.

This module validates bounded export authority and fidelity metadata. It does not
perform live ingestion, licensing, contribution scoring, or payout operations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

FIDELITY = {"exact", "semantic_reconstruction", "inference", "integrity_only", "unavailable"}
RETENTION = {"integrity_only", "reconstructable", "full_fidelity"}
PROHIBITED_PREFIXES = ("03_Records/", "_Policy/")


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def validate_export(bundle: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    required = {"schema_version", "export_id", "source", "authorization", "evidence"}
    missing = sorted(required - bundle.keys())
    if missing:
        reasons.append(f"missing_fields:{','.join(missing)}")

    source = bundle.get("source") or {}
    auth = bundle.get("authorization") or {}
    evidence = bundle.get("evidence") or []

    if source.get("repository") != "StegVerse-Labs/continuity-vault-kit":
        reasons.append("source_repository_mismatch")
    if not str(source.get("release", "")).startswith("v"):
        reasons.append("source_release_invalid")
    root = source.get("verification_root")
    if not isinstance(root, str) or len(root) != 64 or any(c not in "0123456789abcdef" for c in root):
        reasons.append("verification_root_invalid")
    if not source.get("event_ids"):
        reasons.append("event_ids_missing")

    if auth.get("status") != "active":
        reasons.append("authorization_not_active")
    if auth.get("destination") != "GCAT-BCAT-Engine/Publisher":
        reasons.append("destination_mismatch")
    if not auth.get("scope"):
        reasons.append("scope_missing")
    if not auth.get("purpose"):
        reasons.append("purpose_missing")
    if not auth.get("receipt_id"):
        reasons.append("source_receipt_missing")
    if auth.get("revoked") is True:
        reasons.append("authorization_revoked")

    seen_subjects: set[str] = set()
    for index, item in enumerate(evidence):
        prefix = f"evidence[{index}]"
        subject = item.get("subject_id")
        if not subject:
            reasons.append(f"{prefix}:subject_id_missing")
        elif subject in seen_subjects:
            reasons.append(f"{prefix}:duplicate_subject_id")
        else:
            seen_subjects.add(subject)

        fidelity = item.get("fidelity")
        retention = item.get("retention_class")
        payload_available = item.get("payload_available")
        path = item.get("path", "")

        if fidelity not in FIDELITY:
            reasons.append(f"{prefix}:fidelity_invalid")
        if retention not in RETENTION:
            reasons.append(f"{prefix}:retention_class_invalid")
        if fidelity == "exact" and payload_available is not True:
            reasons.append(f"{prefix}:exact_payload_unavailable")
        if fidelity in {"integrity_only", "unavailable"} and payload_available is True:
            reasons.append(f"{prefix}:payload_availability_contradiction")
        if item.get("derived_index") is True:
            reasons.append(f"{prefix}:derived_index_not_canonical")
        if item.get("superseded") is None:
            reasons.append(f"{prefix}:supersession_missing")
        if not item.get("content_hash"):
            reasons.append(f"{prefix}:content_hash_missing")
        if any(path.startswith(value) for value in PROHIBITED_PREFIXES):
            reasons.append(f"{prefix}:prohibited_path")
        if item.get("restricted") is True or item.get("contains_credentials") is True:
            reasons.append(f"{prefix}:restricted_content")

    admitted = not reasons
    receipt = {
        "schema_version": "0.1",
        "receipt_type": "publisher.continuity_export_admission",
        "export_id": bundle.get("export_id"),
        "source_release": source.get("release"),
        "verification_root": root,
        "result": "ADMITTED" if admitted else "REJECTED",
        "reasons": reasons,
        "evidence_count": len(evidence),
        "authority_receipt_id": auth.get("receipt_id"),
    }
    receipt["receipt_sha256"] = sha256(receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--receipt-out", type=Path)
    args = parser.parse_args()
    bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
    receipt = validate_export(bundle)
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.receipt_out:
        args.receipt_out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if receipt["result"] == "ADMITTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
