import copy
import json
from pathlib import Path

from publication_plane.core.receipt_writer import PublicationReceiptWriter
from publisher.governed_outbound_communication import admit_outbound_communication


def contract():
    digest = "a" * 64
    return {
        "schema": "stegverse.publisher.governed-outbound-communication/v1",
        "communication_event": {
            "event_id": "source-event-1",
            "source_system": "authoritative-history-source",
            "source_locator": "source://events/1",
            "observed_at": "2026-10-05T00:00:00Z",
            "content_sha256": digest,
            "media_type": "message/rfc822",
            "predecessor_event_ids": ["source-event-0"],
        },
        "context_resolution": {
            "purpose": "reply",
            "policy_id": "purpose-context-policy-v1",
            "required_categories": [
                {
                    "category": "CORRESPONDENCE_HISTORY",
                    "disposition": "VERIFIED",
                    "evidence_refs": ["source://events/1"],
                }
            ],
        },
        "outbound_manifest": {
            "manifest_id": "outbound-1",
            "recipient": "recipient-ref",
            "channel": "email",
            "body_sha256": digest,
            "attachment_sha256": [],
            "requested_transport": "existing-authorized-email-transport",
            "authority_evidence_refs": ["authority://owner/1"],
            "composition_disposition": "ALLOW",
            "send_observation": {
                "observed": False,
                "provider_event_id": None,
                "sent_at": None,
                "receipt_refs": [],
            },
        },
    }


def writer(tmp_path: Path) -> PublicationReceiptWriter:
    return PublicationReceiptWriter(seed="outbound-test", output_dir=str(tmp_path))


def read_receipt(result):
    return json.loads(Path(result["receipt_path"]).read_text(encoding="utf-8"))


def assert_receipt_verifies(receipt_writer, result):
    assert receipt_writer.verify(Path(result["receipt_path"])) is True


def test_allow_produces_existing_publisher_receipt_with_bound_evidence(tmp_path):
    value = contract()
    receipt_writer = writer(tmp_path)
    result = admit_outbound_communication(value, receipt_writer=receipt_writer)
    receipt = read_receipt(result)
    assert_receipt_verifies(receipt_writer, result)

    assert result["disposition"] == "ALLOW"
    assert result["send_executed"] is False
    assert receipt["gate_result"] == "ALLOW"
    assert receipt["status"] == "composition_admission_observed"
    assert receipt["evidence"]["source_locator"] == "source://events/1"
    assert receipt["evidence"]["predecessor_event_ids"] == ["source-event-0"]
    assert receipt["evidence"]["context_evidence"][0]["evidence_refs"] == ["source://events/1"]
    assert receipt["evidence"]["body_sha256"] == "a" * 64
    assert receipt["evidence"]["send_observed"] is False


def test_insufficient_evidence_fails_closed_and_produces_receipt(tmp_path):
    value = contract()
    value["context_resolution"]["required_categories"][0]["disposition"] = "INSUFFICIENT_EVIDENCE"
    value["outbound_manifest"]["composition_disposition"] = "FAIL_CLOSED"

    receipt_writer = writer(tmp_path)
    result = admit_outbound_communication(value, receipt_writer=receipt_writer)
    receipt = read_receipt(result)
    assert_receipt_verifies(receipt_writer, result)

    assert result["disposition"] == "FAIL_CLOSED"
    assert "insufficient_evidence:CORRESPONDENCE_HISTORY" in result["reasons"]
    assert receipt["gate_result"] == "FAIL_CLOSED"
    assert receipt["evidence"]["context_evidence"][0]["disposition"] == "INSUFFICIENT_EVIDENCE"


def test_schema_invalid_input_fails_closed_with_reason_and_receipt(tmp_path):
    value = contract()
    value["outbound_manifest"]["send_observation"]["provider_event_id"] = "not-observed"

    result = admit_outbound_communication(value, receipt_writer=writer(tmp_path))
    receipt = read_receipt(result)

    assert result["disposition"] == "FAIL_CLOSED"
    assert any(reason.startswith("schema_validation_failed:") for reason in result["reasons"])
    assert receipt["gate_result"] == "FAIL_CLOSED"
    assert result["send_executed"] is False


def test_manifest_deny_is_preserved_as_non_allow_receipt(tmp_path):
    value = contract()
    value["outbound_manifest"]["composition_disposition"] = "DENY"

    receipt_writer = writer(tmp_path)
    result = admit_outbound_communication(value, receipt_writer=receipt_writer)
    receipt = read_receipt(result)
    assert_receipt_verifies(receipt_writer, result)

    assert result["disposition"] == "DENY"
    assert receipt["gate_result"] == "DENY"
    assert result["authority_effect"] == "NONE_ADMISSION_EVIDENCE_ONLY"
