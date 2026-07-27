from __future__ import annotations

import hashlib
import json

from marketplace_coinbase_publication import PublicationLedger
from scripts.import_marketplace_coinbase_settlements import process_triplet


def digest(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def packet():
    value = {
        "packet_version": "marketplace-coinbase-settlement-export-v1",
        "intent_id": "intent-publisher-001",
        "intent_digest": "sha256:intent",
        "capital_review_digest": "sha256:review",
        "decision": "ALLOW",
        "execution_status": "EXECUTED",
        "receipt_chain_head": "sha256:head",
        "settlement": {"marketplace_status": "SETTLED"},
        "settlement_record": {"intent_digest": "sha256:intent", "receipt_chain_head": "sha256:head", "marketplace_status": "SETTLED"},
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
        "marketplace_indexed": True,
        "transport_digest": "sha256:first-transport",
        "live_authority_granted": False,
    }
    return {**body, "ack_digest": digest(body)}


def transport(value, ack):
    body = {
        "transport_version": "marketplace-coinbase-transport-v1",
        "packet_digest": value["packet_digest"],
        "intent_id": value["intent_id"],
        "source": "GCAT-BCAT-Engine/Marketplace",
        "destination": "GCAT-BCAT-Engine/Publisher",
        "sequence": 2,
        "previous_transport_digest": ack["transport_digest"],
        "sent_at": "2026-07-27T00:00:00Z",
        "transport_is_authority": False,
        "live_authority_granted": False,
    }
    return {**body, "transport_digest": digest(body)}


def write_triplet(tmp_path, value, ack, receipt):
    p = tmp_path / "intent-publisher-001.settlement.json"
    a = tmp_path / "intent-publisher-001.ack.json"
    t = tmp_path / "intent-publisher-001.publisher-transport.json"
    p.write_text(json.dumps(value))
    a.write_text(json.dumps(ack))
    t.write_text(json.dumps(receipt))
    return p, a, t


def test_runner_accepts_chained_transport_and_persists_receipt(tmp_path):
    value = packet()
    ack = acknowledgement(value)
    p, a, t = write_triplet(tmp_path, value, ack, transport(value, ack))
    result = process_triplet(
        packet_path=p,
        acknowledgement_path=a,
        transport_path=t,
        ledger=PublicationLedger(tmp_path / "ledger.sqlite3"),
        output_dir=tmp_path / "output",
    )
    assert result["result"] == "ACCEPTED"
    assert result["publication_receipt"]["publication_authorized"] is False
    assert (tmp_path / "output" / "intent-publisher-001.publication.json").exists()


def test_runner_rejects_broken_transport_chain(tmp_path):
    value = packet()
    ack = acknowledgement(value)
    receipt = transport(value, ack)
    receipt["previous_transport_digest"] = "sha256:wrong"
    body = {key: item for key, item in receipt.items() if key != "transport_digest"}
    receipt["transport_digest"] = digest(body)
    p, a, t = write_triplet(tmp_path, value, ack, receipt)
    result = process_triplet(
        packet_path=p,
        acknowledgement_path=a,
        transport_path=t,
        ledger=PublicationLedger(tmp_path / "ledger.sqlite3"),
        output_dir=tmp_path / "output",
    )
    assert result["result"] == "REJECTED"
    assert "Publisher transport chain mismatch" in result["findings"]
