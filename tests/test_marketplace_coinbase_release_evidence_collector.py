from __future__ import annotations

import json

from scripts import collect_marketplace_coinbase_release_evidence as collector


def signed(body, field):
    return {**body, field: collector.digest(body)}


def write_bound_evidence(tmp_path, monkeypatch):
    evidence_dir = tmp_path / "evidence"
    crypto_dir = evidence_dir / "crypto_bot"
    marketplace_dir = evidence_dir / "marketplace"
    crypto_dir.mkdir(parents=True)
    marketplace_dir.mkdir(parents=True)
    monkeypatch.setattr(collector, "EVIDENCE_DIR", evidence_dir)

    packet = signed({
        "packet_version": "marketplace-coinbase-settlement-export-v1",
        "intent_id": "intent-collector-001",
        "live_authority_granted": False,
    }, "packet_digest")
    market_transport = signed({
        "transport_version": "marketplace-coinbase-transport-v1",
        "intent_id": packet["intent_id"],
        "packet_digest": packet["packet_digest"],
        "source": "StegVerse-Labs/crypto-bot",
        "destination": "GCAT-BCAT-Engine/Marketplace",
        "sequence": 1,
        "previous_transport_digest": None,
        "transport_is_authority": False,
        "live_authority_granted": False,
    }, "transport_digest")
    ack = signed({
        "ack_version": "marketplace-coinbase-settlement-ack-v1",
        "intent_id": packet["intent_id"],
        "packet_digest": packet["packet_digest"],
        "result": "ACCEPTED",
        "findings": [],
        "marketplace_indexed": True,
        "transport_digest": market_transport["transport_digest"],
        "live_authority_granted": False,
    }, "ack_digest")
    publisher_transport = signed({
        "transport_version": "marketplace-coinbase-transport-v1",
        "intent_id": packet["intent_id"],
        "packet_digest": packet["packet_digest"],
        "source": "GCAT-BCAT-Engine/Marketplace",
        "destination": "GCAT-BCAT-Engine/Publisher",
        "sequence": 2,
        "previous_transport_digest": market_transport["transport_digest"],
        "marketplace_ack_digest": ack["ack_digest"],
        "transport_is_authority": False,
        "live_authority_granted": False,
    }, "transport_digest")

    bindings = {
        "intent_id": packet["intent_id"],
        "packet_digest": packet["packet_digest"],
        "marketplace_transport_digest": market_transport["transport_digest"],
        "marketplace_ack_digest": ack["ack_digest"],
        "publisher_transport_digest": publisher_transport["transport_digest"],
        "publisher_projection_digest": "sha256:projection",
        "publication_receipt_digest": "sha256:receipt",
    }
    cross_body = {
        "manifest_version": "marketplace-coinbase-cross-repository-evidence-v1",
        "result": "PASS",
        "artifact_directory": "release_evidence/cross_repository",
        "artifacts_present": [
            "marketplace_acknowledgement",
            "marketplace_transport",
            "publication_receipt",
            "publisher_projection",
            "publisher_transport",
            "settlement_packet",
        ],
        "evidence_bindings": bindings,
        "findings": [],
        "live_authority_granted": False,
    }
    cross = {**cross_body, "manifest_digest": collector.digest(cross_body)}
    readiness_body = {
        "receipt_type": "paper_release_readiness",
        "cross_repository_evidence_digest": cross["manifest_digest"],
        "release_decision": "PAPER_RELEASE_READY",
        "live_authority": "NOT_GRANTED",
    }
    readiness = {**readiness_body, "receipt_digest": collector.digest(readiness_body)}

    (crypto_dir / "PAPER_RELEASE_READINESS.json").write_text(json.dumps(readiness))
    (crypto_dir / "CROSS_REPOSITORY_EVIDENCE.json").write_text(json.dumps(cross))
    (marketplace_dir / "intent.settlement.json").write_text(json.dumps(packet))
    (marketplace_dir / "intent.transport.json").write_text(json.dumps(market_transport))
    (marketplace_dir / "intent.ack.json").write_text(json.dumps(ack))
    (marketplace_dir / "intent.publisher.transport.json").write_text(json.dumps(publisher_transport))
    return ack, marketplace_dir


def test_missing_token_writes_pending_credential(tmp_path, monkeypatch):
    monkeypatch.setattr(collector, "TOKEN", "")
    monkeypatch.setattr(collector, "OUTPUT", tmp_path / "status.json")
    result = collector.main()
    status = json.loads((tmp_path / "status.json").read_text())
    assert result == 0
    assert status["status"] == "PENDING_CREDENTIAL"
    assert status["paper_release_verified"] is False
    assert status["publication_authorized"] is False
    assert status["release_authorized"] is False
    assert status["execution_authorized"] is False
    assert status["live_authority_granted"] is False


def test_status_digest_is_bound(tmp_path, monkeypatch):
    monkeypatch.setattr(collector, "OUTPUT", tmp_path / "status.json")
    collector.write("REJECTED", "test", {"source": {"state": "INVALID"}}, ["bad"])
    status = json.loads((tmp_path / "status.json").read_text())
    body = {key: value for key, value in status.items() if key != "status_digest"}
    assert status["status_digest"] == collector.digest(body)
    assert status["manual_user_action_required"] is False


def test_marketplace_artifact_matches_manifest_bindings(tmp_path, monkeypatch):
    write_bound_evidence(tmp_path, monkeypatch)
    assert collector.validate_crypto_evidence() == []
    assert collector.validate_marketplace_evidence() == []


def test_marketplace_ack_tampering_is_rejected(tmp_path, monkeypatch):
    ack, marketplace_dir = write_bound_evidence(tmp_path, monkeypatch)
    ack["result"] = "REJECTED"
    ack["ack_digest"] = collector.digest(collector.without(ack, "ack_digest"))
    (marketplace_dir / "intent.ack.json").write_text(json.dumps(ack))
    failures = collector.validate_marketplace_evidence()
    assert "marketplace_ack_binding_mismatch" in failures
    assert "transport_ack_binding_mismatch" in failures
    assert "marketplace_ack_not_accepted_and_indexed" in failures
