#!/usr/bin/env python3
"""Verify bounded connected-GitHub evidence without persisting private source files."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RELAY_PATH = ROOT / "data" / "marketplace-coinbase-connected-relay.json"
OUTPUT = ROOT / "data" / "marketplace-coinbase-release-evidence-status.json"
REQUIRED_BINDINGS = (
    "intent_id",
    "packet_digest",
    "marketplace_transport_digest",
    "marketplace_ack_digest",
    "publisher_transport_digest",
    "publisher_projection_digest",
    "publication_receipt_digest",
)


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value)).hexdigest()


def without(value: dict[str, Any], field: str) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != field}


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def validate_relay(relay: dict[str, Any], publication: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    if relay.get("schema") != "stegverse.publisher.marketplace_coinbase_connected_relay.v1":
        findings.append("connected_relay_schema_mismatch")
    if relay.get("relay_digest") != digest(without(relay, "relay_digest")):
        findings.append("connected_relay_digest_mismatch")
    for field in (
        "publication_authorized",
        "release_authorized",
        "execution_authorized",
        "live_authority_granted",
        "manual_user_action_required",
    ):
        expected = False
        if relay.get(field) is not expected:
            findings.append(f"connected_relay_{field}_boundary_invalid")

    crypto = relay.get("crypto_bot") or {}
    if crypto.get("repository") != "StegVerse-Labs/crypto-bot":
        findings.append("crypto_source_repository_mismatch")
    if crypto.get("source_transport") != "actions_artifact":
        findings.append("crypto_source_transport_mismatch")
    if crypto.get("source_evidence_kind") != "first_accessibility_mark":
        findings.append("crypto_source_evidence_kind_mismatch")
    if not str(crypto.get("artifact", "")).startswith("first-accessibility-mark-"):
        findings.append("crypto_source_artifact_mismatch")
    if not crypto.get("artifact_id") or not crypto.get("workflow_run_id") or not crypto.get("head_sha"):
        findings.append("crypto_source_identity_missing")
    for field in ("artifact_digest", "observed_receipt_digest", "manifest_digest"):
        if not str(crypto.get(field, "")).startswith("sha256:"):
            findings.append(f"crypto_{field}_missing")
    if crypto.get("ci_tests") != "PASS":
        findings.append("crypto_ci_tests_not_pass")
    if crypto.get("paper_runtime") != "IMPLEMENTED" or crypto.get("paper_trading_accessible") is not True:
        findings.append("crypto_paper_runtime_not_accessible")
    if crypto.get("release_decision") != "PAPER_RELEASE_BLOCKED_PENDING_CROSS_REPOSITORY_EVIDENCE":
        findings.append("crypto_readiness_decision_invalid")
    if crypto.get("live_authority") != "NOT_GRANTED":
        findings.append("crypto_live_authority_boundary_invalid")

    marketplace = relay.get("marketplace") or {}
    if marketplace.get("repository") != "GCAT-BCAT-Engine/Marketplace":
        findings.append("marketplace_source_repository_mismatch")
    if marketplace.get("source_transport") != "connected_github_repository_relay":
        findings.append("marketplace_source_transport_mismatch")
    if marketplace.get("artifact") != "repository-committed-marketplace-evidence":
        findings.append("marketplace_source_artifact_mismatch")
    if not marketplace.get("head_sha") or not marketplace.get("collection_status_commit"):
        findings.append("marketplace_source_commit_missing")
    expected_marketplace_relay = digest(without(marketplace, "relay_receipt_digest"))
    if marketplace.get("relay_receipt_digest") != expected_marketplace_relay:
        findings.append("marketplace_relay_receipt_digest_mismatch")
    for field in (
        "packet_file_sha256",
        "sequence_1_file_sha256",
        "ack_file_sha256",
        "sequence_2_file_sha256",
    ):
        value = marketplace.get(field)
        if not isinstance(value, str) or len(value) != 64:
            findings.append(f"marketplace_{field}_invalid")

    bindings = relay.get("evidence_bindings")
    if not isinstance(bindings, dict):
        findings.append("connected_relay_bindings_missing")
        bindings = {}
    for field in REQUIRED_BINDINGS:
        if not bindings.get(field):
            findings.append(f"connected_relay_binding_missing:{field}")

    if publication.get("result") not in {"ACCEPTED", "DUPLICATE"}:
        findings.append("publisher_publication_not_accepted")
    projection = publication.get("projection") or {}
    receipt = publication.get("publication_receipt") or {}
    if projection.get("projection_digest") != digest(without(projection, "projection_digest")):
        findings.append("publisher_projection_digest_mismatch")
    if receipt.get("receipt_digest") != digest(without(receipt, "receipt_digest")):
        findings.append("publisher_publication_receipt_digest_mismatch")
    if projection.get("paper_evidence_verified") is not True:
        findings.append("publisher_projection_not_verified")
    if receipt.get("result") not in {"ACCEPTED", "DUPLICATE"}:
        findings.append("publisher_receipt_not_accepted")
    for value, label in ((projection, "projection"), (receipt, "receipt")):
        if value.get("publication_authorized") is not False:
            findings.append(f"publisher_{label}_publication_authority_invalid")
        if value.get("release_authorized") is not False:
            findings.append(f"publisher_{label}_release_authority_invalid")
        if value.get("live_authority_granted") is not False:
            findings.append(f"publisher_{label}_live_authority_invalid")

    comparisons = (
        (projection.get("intent_id"), bindings.get("intent_id"), "projection_intent_binding_mismatch"),
        (projection.get("packet_digest"), bindings.get("packet_digest"), "projection_packet_binding_mismatch"),
        (projection.get("marketplace_ack_digest"), bindings.get("marketplace_ack_digest"), "projection_ack_binding_mismatch"),
        (projection.get("projection_digest"), bindings.get("publisher_projection_digest"), "projection_digest_binding_mismatch"),
        (receipt.get("intent_id"), bindings.get("intent_id"), "receipt_intent_binding_mismatch"),
        (receipt.get("packet_digest"), bindings.get("packet_digest"), "receipt_packet_binding_mismatch"),
        (receipt.get("marketplace_ack_digest"), bindings.get("marketplace_ack_digest"), "receipt_ack_binding_mismatch"),
        (receipt.get("transport_digest"), bindings.get("publisher_transport_digest"), "receipt_transport_binding_mismatch"),
        (receipt.get("projection_digest"), bindings.get("publisher_projection_digest"), "receipt_projection_binding_mismatch"),
        (receipt.get("receipt_digest"), bindings.get("publication_receipt_digest"), "receipt_digest_binding_mismatch"),
    )
    for actual, expected, message in comparisons:
        if actual != expected:
            findings.append(message)
    return sorted(set(findings))


def build_status(relay: dict[str, Any], findings: list[str]) -> dict[str, Any]:
    crypto = relay.get("crypto_bot") or {}
    marketplace = relay.get("marketplace") or {}
    status = "VERIFIED" if not findings else "REJECTED"
    sources = {
        "crypto_bot": {
            "state": "PASS" if not findings else "INVALID",
            "repository": crypto.get("repository"),
            "artifact": crypto.get("artifact"),
            "artifact_id": crypto.get("artifact_id"),
            "artifact_digest": crypto.get("artifact_digest"),
            "workflow_run_id": crypto.get("workflow_run_id"),
            "head_sha": crypto.get("head_sha"),
            "source_transport": crypto.get("source_transport"),
            "source_evidence_kind": crypto.get("source_evidence_kind"),
        },
        "marketplace": {
            "state": "PASS" if not findings else "INVALID",
            "repository": marketplace.get("repository"),
            "artifact": marketplace.get("artifact"),
            "head_sha": marketplace.get("head_sha"),
            "source_transport": marketplace.get("source_transport"),
            "relay_receipt_digest": marketplace.get("relay_receipt_digest"),
        },
    }
    body = {
        "schema": "stegverse.publisher.marketplace_coinbase_release_evidence.v2",
        "status": status,
        "reason": (
            "publisher_reconstructed_hash_bound_paper_release_evidence_via_connected_relay"
            if not findings
            else "connected_relay_evidence_not_verified"
        ),
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "sources": sources,
        "failures": findings,
        "evidence_bindings": relay.get("evidence_bindings") or {},
        "crypto_repository_readiness_receipt_digest": crypto.get("observed_receipt_digest"),
        "crypto_repository_manifest_digest": crypto.get("manifest_digest"),
        "paper_release_verified": status == "VERIFIED",
        "publication_authorized": False,
        "release_authorized": False,
        "execution_authorized": False,
        "live_authority_granted": False,
        "manual_user_action_required": False,
    }
    return {**body, "status_digest": digest(body)}


def verify_paths(relay: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    raw_path = relay.get("publisher_publication_path")
    if not isinstance(raw_path, str):
        return {}, ["publisher_publication_path_missing"]
    publication_path = (ROOT / raw_path).resolve()
    if ROOT.resolve() not in publication_path.parents or not publication_path.is_file():
        return {}, ["publisher_publication_path_invalid"]
    publication = load_object(publication_path)
    return publication, validate_relay(relay, publication)


def main() -> int:
    if not RELAY_PATH.exists():
        print("MARKETPLACE_COINBASE_CONNECTED_RELAY_NOT_PRESENT")
        return 3
    relay = load_object(RELAY_PATH)
    publication, findings = verify_paths(relay)
    payload = build_status(relay, findings)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("MARKETPLACE_COINBASE_CONNECTED_RELAY_VERIFIED" if not findings else "MARKETPLACE_COINBASE_CONNECTED_RELAY_REJECTED")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
