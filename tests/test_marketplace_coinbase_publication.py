from __future__ import annotations

import hashlib
import json

from marketplace_coinbase_publication import PublicationLedger


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value):
    return "sha256:" + hashlib.sha256(canonical(value)).hexdigest()


def packet():
    value = {
        "packet_version": "marketplace-coinbase-settlement-export-v1",
        "generated_at": "2026-07-27T00:00:00Z",
        "intent_id": "intent-publish-001",
        "intent_digest": "sha256:intent",
        "capital_review_digest": "sha256:review",
        "decision": "ALLOW",
        "execution_status": "EXECUTED",
        "receipt_chain_head": "sha256:chain",
        "settlement": {"marketplace_status": "SETTLED"},
        "settlement_record": {"intent_id": "intent-publish-001"},
        "destinations": ["GCAT-BCAT-Engine/Marketplace", "GCAT-BCAT-Engine/Publisher"],
        "live_authority_granted": False,
    }
    value["packet_digest"] = digest(value)
    return value


def acknowledgement(value):
    body = {
        "ack_version": "marketplace-coinbase-settlement-ack-v1",
        "intent_id": value["intent_id"],
        "packet_digest": value["packet_digest"],
        "result": "ACCEPTED",
        "findings": [],
        "recorded_at": "2026-07-27T00:01:00Z",
        "marketplace_indexed": True,
        "live_authority_granted": False,
    }
    return {**body, "ack_digest": digest(body)}


def test_accepts_verified_packet_and_acknowledgement(tmp_path):
    value = packet()
    result = PublicationLedger(tmp_path / "publication.sqlite3").ingest(value, acknowledgement(value))
    assert result["result"] == "ACCEPTED"
    assert result["projection"]["paper_evidence_verified"] is True
    assert result["projection"]["publication_authorized"] is False
    assert result["projection"]["live_authority_granted"] is False


def test_missing_acknowledgement_is_rejected(tmp_path):
    result = PublicationLedger(tmp_path / "publication.sqlite3").ingest(packet(), None)
    assert result["result"] == "REJECTED"
    assert "Marketplace acknowledgement missing" in result["findings"]


def test_ack_digest_mismatch_is_rejected(tmp_path):
    value = packet()
    ack = acknowledgement(value)
    ack["ack_digest"] = "sha256:wrong"
    result = PublicationLedger(tmp_path / "publication.sqlite3").ingest(value, ack)
    assert result["result"] == "REJECTED"
    assert "Marketplace acknowledgement digest mismatch" in result["findings"]


def test_false_live_claim_is_rejected(tmp_path):
    value = packet()
    value["live_authority_granted"] = True
    unsigned = {key: item for key, item in value.items() if key != "packet_digest"}
    value["packet_digest"] = digest(unsigned)
    result = PublicationLedger(tmp_path / "publication.sqlite3").ingest(value, acknowledgement(value))
    assert result["result"] == "REJECTED"
    assert "paper settlement packet claims live authority" in result["findings"]


def test_duplicate_is_idempotent(tmp_path):
    value = packet()
    ack = acknowledgement(value)
    ledger = PublicationLedger(tmp_path / "publication.sqlite3")
    assert ledger.ingest(value, ack)["result"] == "ACCEPTED"
    assert ledger.ingest(value, ack)["result"] == "DUPLICATE"
