from __future__ import annotations

import copy
import json
from pathlib import Path

from scripts.verify_marketplace_coinbase_connected_relay import digest, validate_relay, without

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_committed_connected_relay_and_publication_validate():
    relay = load("data/marketplace-coinbase-connected-relay.json")
    publication = load(relay["publisher_publication_path"])
    assert validate_relay(relay, publication) == []


def test_authority_escalation_fails_even_with_recomputed_relay_digest():
    relay = load("data/marketplace-coinbase-connected-relay.json")
    publication = load(relay["publisher_publication_path"])
    tampered = copy.deepcopy(relay)
    tampered["live_authority_granted"] = True
    tampered["relay_digest"] = digest(without(tampered, "relay_digest"))
    findings = validate_relay(tampered, publication)
    assert "connected_relay_live_authority_granted_boundary_invalid" in findings


def test_publication_digest_tampering_fails_closed():
    relay = load("data/marketplace-coinbase-connected-relay.json")
    publication = load(relay["publisher_publication_path"])
    tampered = copy.deepcopy(publication)
    tampered["projection"]["packet_digest"] = "sha256:tampered"
    findings = validate_relay(relay, tampered)
    assert "publisher_projection_digest_mismatch" in findings
    assert "projection_packet_binding_mismatch" in findings
