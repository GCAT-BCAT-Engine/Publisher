"""Structural admission for evaluator-facing evidence reports on the existing Publisher pipeline.

Does not claim a KV origin, confer publication approval or create Master Records.
The source request is explicitly distinguished from authenticated custody.
"""
from __future__ import annotations
import hashlib
import json
from typing import Any

REPORT_SCHEMA = "stegverse.publisher.evidence-report-package/v1"

class EvaluatorReportError(ValueError):
    pass

def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def validate_evaluator_report(bundle: dict[str, Any]) -> dict[str, Any]:
    if bundle.get("schema_version") != REPORT_SCHEMA:
        raise EvaluatorReportError("incorrect generic evaluator-report schema")
    auth = bundle.get("authorization") or {}
    if (auth.get("status") != "active"
        or auth.get("destination") != "GCAT-BCAT-Engine/Publisher"
        or auth.get("purpose") != "EXTERNAL_EVALUATOR_REVIEW"
        or auth.get("revoked") is not False
        or not isinstance(auth.get("authority_ref"), str)
        or not auth["authority_ref"]):
        raise EvaluatorReportError("explicit bounded review instruction required")
    if not isinstance(auth.get("scope"), list) or not auth["scope"]:
        raise EvaluatorReportError("review scope required")
    redaction = bundle.get("redaction") or {}
    if (redaction.get("review_state") != "OWNER_APPROVED"
        or redaction.get("restricted_content_present") is not False):
        raise EvaluatorReportError("owner review/redaction must be declared")
    source = bundle.get("source") or {}
    if not source.get("repository") or not source.get("release") or not source.get("verification_root"):
        raise EvaluatorReportError("source provenance required")
    if not isinstance(source.get("event_ids"), list) or not source["event_ids"]:
        raise EvaluatorReportError("source evidence identities required")
    items = bundle.get("evidence")
    if not isinstance(items, list) or not items:
        raise EvaluatorReportError("report evidence inventory required")
    seen = set()
    for item in items:
        subject = item.get("subject_id")
        if not isinstance(subject, str) or not subject or subject in seen:
            raise EvaluatorReportError("unique source evidence identities required")
        seen.add(subject)
        if not item.get("path") or not item.get("content_hash"):
            raise EvaluatorReportError("source evidence path/hash required")
        if item.get("fidelity") not in {"exact", "semantic_reconstruction", "inference", "integrity_only", "unavailable"}:
            raise EvaluatorReportError("invalid evidence fidelity")
        if item.get("restricted") is not False or item.get("contains_credentials") is not False:
            raise EvaluatorReportError("restricted evidence not admitted")
        if item.get("derived_index") is not False or item.get("superseded") is not False:
            raise EvaluatorReportError("index-only or superseded source not admitted")
    result = {
        "schema_version": "0.1",
        "receipt_type": "publisher.evaluator_report_source_admission",
        "export_id": bundle.get("export_id"),
        "source_release": source["release"],
        "verification_root": source["verification_root"],
        "result": "ADMITTED",
        "basis": "SOURCE_DECLARATION_ONLY_NOT_AUTHENTIC_GOVERNED_TRANSITION",
        "evidence_count": len(items),
        "authority_ref": auth["authority_ref"],
        "publication_authorized": False,
        "release_authorized": False,
        "execution_authorized": False,
        "authority_effect": "NONE",
    }
    result["receipt_sha256"] = digest(result)
    return result
