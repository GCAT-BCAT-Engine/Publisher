from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PACKET_VERSION = "marketplace-coinbase-settlement-export-v1"
ACK_VERSION = "marketplace-coinbase-settlement-ack-v1"
PUBLISHER_DESTINATION = "GCAT-BCAT-Engine/Publisher"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value)).hexdigest()


def _without(value: dict[str, Any], field: str) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != field}


def verify_for_publication(packet: dict[str, Any], acknowledgement: dict[str, Any] | None) -> list[str]:
    findings: list[str] = []
    if packet.get("packet_version") != PACKET_VERSION:
        findings.append("unsupported settlement packet version")
    if packet.get("packet_digest") != _sha256(_without(packet, "packet_digest")):
        findings.append("settlement packet digest mismatch")
    destinations = packet.get("destinations")
    if not isinstance(destinations, list) or PUBLISHER_DESTINATION not in destinations:
        findings.append("Publisher destination missing")
    if packet.get("live_authority_granted") is not False:
        findings.append("paper settlement packet claims live authority")
    if packet.get("execution_status") != "EXECUTED":
        findings.append("execution status is not EXECUTED")
    if packet.get("decision") != "ALLOW":
        findings.append("StegFin decision is not ALLOW")

    if acknowledgement is None:
        findings.append("Marketplace acknowledgement missing")
        return findings
    if acknowledgement.get("ack_version") != ACK_VERSION:
        findings.append("unsupported Marketplace acknowledgement version")
    if acknowledgement.get("ack_digest") != _sha256(_without(acknowledgement, "ack_digest")):
        findings.append("Marketplace acknowledgement digest mismatch")
    if acknowledgement.get("packet_digest") != packet.get("packet_digest"):
        findings.append("acknowledgement packet digest mismatch")
    if acknowledgement.get("intent_id") != packet.get("intent_id"):
        findings.append("acknowledgement intent mismatch")
    if acknowledgement.get("result") not in {"ACCEPTED", "DUPLICATE"}:
        findings.append("Marketplace acknowledgement did not accept packet")
    if acknowledgement.get("marketplace_indexed") is not True:
        findings.append("Marketplace settlement was not indexed")
    if acknowledgement.get("live_authority_granted") is not False:
        findings.append("Marketplace acknowledgement claims live authority")
    return findings


@dataclass(frozen=True)
class PublicationLedger:
    path: Path

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.execute(
            "CREATE TABLE IF NOT EXISTS publications ("
            "intent_id TEXT PRIMARY KEY, packet_digest TEXT NOT NULL, ack_digest TEXT NOT NULL, "
            "projection_digest TEXT NOT NULL, projection_json TEXT NOT NULL, recorded_at TEXT NOT NULL)"
        )
        connection.commit()
        return connection

    def ingest(self, packet: dict[str, Any], acknowledgement: dict[str, Any] | None) -> dict[str, Any]:
        findings = verify_for_publication(packet, acknowledgement)
        intent_id = str(packet.get("intent_id") or "")
        packet_digest = str(packet.get("packet_digest") or "")
        ack_digest = str((acknowledgement or {}).get("ack_digest") or "")
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        result = "REJECTED" if findings else "ACCEPTED"

        projection_body = {
            "projection_version": "marketplace-coinbase-publication-v1",
            "intent_id": intent_id,
            "packet_digest": packet_digest,
            "marketplace_ack_digest": ack_digest,
            "marketplace_status": (packet.get("settlement") or {}).get("marketplace_status"),
            "execution_status": packet.get("execution_status"),
            "paper_evidence_verified": not findings,
            "publication_authorized": False,
            "release_authorized": False,
            "live_authority_granted": False,
            "recorded_at": now,
            "findings": findings,
        }
        projection = {**projection_body, "projection_digest": _sha256(projection_body)}

        with self._connect() as connection:
            existing = connection.execute(
                "SELECT packet_digest, ack_digest, projection_digest, projection_json FROM publications WHERE intent_id = ?",
                (intent_id,),
            ).fetchone()
            if not findings and existing:
                if existing[0] == packet_digest and existing[1] == ack_digest:
                    result = "DUPLICATE"
                    return {"result": result, "projection": json.loads(existing[3]), "findings": []}
                result = "REJECTED"
                findings.append("conflicting publication state for existing intent")
                projection_body["paper_evidence_verified"] = False
                projection_body["findings"] = findings
                projection = {**projection_body, "projection_digest": _sha256(projection_body)}

            if result == "ACCEPTED":
                connection.execute(
                    "INSERT INTO publications(intent_id, packet_digest, ack_digest, projection_digest, projection_json, recorded_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (intent_id, packet_digest, ack_digest, projection["projection_digest"], json.dumps(projection, sort_keys=True), now),
                )
                connection.commit()

        return {"result": result, "projection": projection, "findings": findings}
