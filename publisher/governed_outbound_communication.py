"""Admission binding for governed outbound communication v1.

Consumes a supplied, already-resolved communication contract. It does not retrieve
history, compose content, send media, resolve credentials, or create authority.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from publication_plane.core.receipt_writer import PublicationReceiptWriter

SCHEMA_NAME = "stegverse.publisher.governed-outbound-communication/v1"
MODULE = "publisher.governed_outbound_communication"
DESTINATION = "GCAT-BCAT-Engine/Publisher"
_ALLOWED_CONTEXT = {"VERIFIED", "NOT_APPLICABLE", "NO_PRIOR_HISTORY"}
_SCHEMA_PATH = Path(__file__).parents[1] / "schemas" / "publisher-governed-outbound-communication.v1.schema.json"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _validator() -> Draft202012Validator:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def evaluate_outbound_communication(value: Mapping[str, Any]) -> dict[str, Any]:
    """Return an explicit admission disposition without performing side effects."""
    if not isinstance(value, Mapping):
        return {"disposition": "FAIL_CLOSED", "reasons": ["contract_required"]}

    instance = dict(value)
    errors = sorted(_validator().iter_errors(instance), key=lambda error: list(error.absolute_path))
    if errors:
        return {
            "disposition": "FAIL_CLOSED",
            "reasons": ["schema_validation_failed:" + error.message for error in errors],
        }

    categories = instance["context_resolution"]["required_categories"]
    unresolved = [
        item["category"]
        for item in categories
        if item["disposition"] not in _ALLOWED_CONTEXT
    ]
    if unresolved:
        return {
            "disposition": "FAIL_CLOSED",
            "reasons": ["insufficient_evidence:" + category for category in unresolved],
        }

    requested = instance["outbound_manifest"]["composition_disposition"]
    if requested != "ALLOW":
        return {
            "disposition": requested,
            "reasons": ["manifest_requested_" + requested.lower()],
        }

    return {"disposition": "ALLOW", "reasons": []}


def admit_outbound_communication(
    value: Mapping[str, Any],
    *,
    receipt_writer: PublicationReceiptWriter,
) -> dict[str, Any]:
    """Evaluate and retain the transition using the existing Publisher receipt writer."""
    evaluation = evaluate_outbound_communication(value)
    instance = dict(value) if isinstance(value, Mapping) else {}
    context = instance.get("context_resolution") if isinstance(instance.get("context_resolution"), Mapping) else {}
    manifest = instance.get("outbound_manifest") if isinstance(instance.get("outbound_manifest"), Mapping) else {}
    event = instance.get("communication_event") if isinstance(instance.get("communication_event"), Mapping) else {}

    evidence = {
        "contract_schema": instance.get("schema"),
        "contract_sha256": _sha256(instance),
        "purpose": context.get("purpose"),
        "policy_id": context.get("policy_id"),
        "context_evidence": [
            {
                "category": item.get("category"),
                "disposition": item.get("disposition"),
                "evidence_refs": item.get("evidence_refs", []),
            }
            for item in context.get("required_categories", [])
            if isinstance(item, Mapping)
        ],
        "source_event_id": event.get("event_id"),
        "source_locator": event.get("source_locator"),
        "source_content_sha256": event.get("content_sha256"),
        "predecessor_event_ids": event.get("predecessor_event_ids", []),
        "manifest_id": manifest.get("manifest_id"),
        "body_sha256": manifest.get("body_sha256"),
        "attachment_sha256": manifest.get("attachment_sha256", []),
        "requested_transport": manifest.get("requested_transport"),
        "authority_evidence_refs": manifest.get("authority_evidence_refs", []),
        "send_observed": (manifest.get("send_observation") or {}).get("observed"),
        "reasons": evaluation["reasons"],
    }

    receipt_path = receipt_writer.write(
        gate_result=evaluation["disposition"],
        confidence=1.0 if evaluation["disposition"] == "ALLOW" else 0.0,
        evidence=evidence,
        module=MODULE,
        destination=DESTINATION,
        status="composition_admission_observed",
    )
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    return {
        "schema": "stegverse.publisher.governed-outbound-communication-admission/v1",
        "disposition": evaluation["disposition"],
        "reasons": evaluation["reasons"],
        "receipt_id": receipt["receipt_id"],
        "receipt_path": str(receipt_path),
        "send_executed": False,
        "authority_effect": "NONE_ADMISSION_EVIDENCE_ONLY",
    }
