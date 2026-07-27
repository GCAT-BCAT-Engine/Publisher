from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from marketplace_coinbase_publication import PublicationLedger

SOURCE = "GCAT-BCAT-Engine/Marketplace"
DESTINATION = "GCAT-BCAT-Engine/Publisher"
TRANSPORT_VERSION = "marketplace-coinbase-transport-v1"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value)).hexdigest()


def verify_transport(receipt: dict[str, Any], packet: dict[str, Any], acknowledgement: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    body = {key: value for key, value in receipt.items() if key != "transport_digest"}
    if receipt.get("transport_version") != TRANSPORT_VERSION:
        findings.append("unsupported transport version")
    if receipt.get("transport_digest") != _digest(body):
        findings.append("transport digest mismatch")
    if receipt.get("source") != SOURCE:
        findings.append("unexpected transport source")
    if receipt.get("destination") != DESTINATION:
        findings.append("unexpected transport destination")
    if receipt.get("packet_digest") != packet.get("packet_digest"):
        findings.append("transport packet digest mismatch")
    if receipt.get("intent_id") != packet.get("intent_id"):
        findings.append("transport intent mismatch")
    if receipt.get("sequence") != 2:
        findings.append("Publisher transport sequence must be 2")
    if receipt.get("previous_transport_digest") != acknowledgement.get("transport_digest"):
        findings.append("Publisher transport chain mismatch")
    if receipt.get("transport_is_authority") is not False:
        findings.append("transport asserted authority")
    if receipt.get("live_authority_granted") is not False:
        findings.append("transport asserted live authority")
    return findings


def process_triplet(*, packet_path: Path, acknowledgement_path: Path, transport_path: Path, ledger: PublicationLedger, output_dir: Path) -> dict[str, Any]:
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    acknowledgement = json.loads(acknowledgement_path.read_text(encoding="utf-8"))
    transport = json.loads(transport_path.read_text(encoding="utf-8"))
    transport_findings = verify_transport(transport, packet, acknowledgement)

    if transport_findings:
        result = {
            "result": "REJECTED",
            "findings": transport_findings,
            "projection": {
                "projection_version": "marketplace-coinbase-publication-v1",
                "intent_id": packet.get("intent_id"),
                "packet_digest": packet.get("packet_digest"),
                "marketplace_ack_digest": acknowledgement.get("ack_digest"),
                "paper_evidence_verified": False,
                "publication_authorized": False,
                "release_authorized": False,
                "live_authority_granted": False,
            },
        }
    else:
        result = ledger.ingest(packet, acknowledgement)

    receipt_body = {
        "receipt_version": "marketplace-coinbase-publication-receipt-v1",
        "intent_id": packet.get("intent_id"),
        "packet_digest": packet.get("packet_digest"),
        "marketplace_ack_digest": acknowledgement.get("ack_digest"),
        "transport_digest": transport.get("transport_digest"),
        "result": result.get("result"),
        "projection_digest": (result.get("projection") or {}).get("projection_digest"),
        "publication_authorized": False,
        "release_authorized": False,
        "live_authority_granted": False,
        "findings": result.get("findings", []),
    }
    publication_receipt = {**receipt_body, "receipt_digest": _digest(receipt_body)}
    result["publication_receipt"] = publication_receipt

    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{packet.get('intent_id')}.publication.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inbox", default="incoming/marketplace-coinbase")
    parser.add_argument("--ledger", default="data/marketplace-coinbase-publications.sqlite3")
    parser.add_argument("--output", default="data/marketplace-coinbase-publications")
    args = parser.parse_args()

    inbox = Path(args.inbox)
    ledger = PublicationLedger(Path(args.ledger))
    processed = 0
    rejected = 0
    for packet_path in sorted(inbox.glob("*.settlement.json")):
        stem = packet_path.name.replace(".settlement.json", "")
        acknowledgement_path = inbox / f"{stem}.ack.json"
        transport_path = inbox / f"{stem}.publisher-transport.json"
        if not acknowledgement_path.exists() or not transport_path.exists():
            rejected += 1
            continue
        result = process_triplet(
            packet_path=packet_path,
            acknowledgement_path=acknowledgement_path,
            transport_path=transport_path,
            ledger=ledger,
            output_dir=Path(args.output),
        )
        processed += 1
        rejected += int(result.get("result") == "REJECTED")
    print(json.dumps({"processed": processed, "rejected": rejected}, sort_keys=True))
    return 1 if rejected else 0


if __name__ == "__main__":
    raise SystemExit(main())
