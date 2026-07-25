#!/usr/bin/env python3
"""Validate Publisher visibility and authority envelopes without inference.

Public visibility is descriptive and never grants publication, attribution,
endorsement, interoperability, compatibility, or external-association authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Mapping


class PublicationAuthorityError(ValueError):
    """Raised when a publication envelope violates an authority boundary."""


AUTHORITY_FIELDS = (
    "claim_authority",
    "publication_authority",
    "attribution_authority",
    "public_association_authority",
)
CLAIM_FIELDS = ("endorsement", "compatibility", "interoperability")
VISIBILITY_STATES = {"PRIVATE", "RESTRICTED", "PUBLICLY_VISIBLE"}
PROCESS_STATES = {"DRAFT", "REVIEW_ONLY", "ADOPTED", "WITHDRAWN", "SUPERSEDED"}


def _canonical(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PublicationAuthorityError(f"{field} must be a non-empty string")
    return value.strip()


def validate_envelope(envelope: Mapping[str, Any]) -> Dict[str, Any]:
    required = {
        "schema_version",
        "artifact_id",
        "artifact_version",
        "visibility_state",
        "process_state",
        *AUTHORITY_FIELDS,
        *CLAIM_FIELDS,
        "external_references",
        "requested_publication_action",
    }
    missing = sorted(required - set(envelope))
    if missing:
        raise PublicationAuthorityError(f"missing required fields: {', '.join(missing)}")

    normalized: Dict[str, Any] = dict(envelope)
    for field in ("schema_version", "artifact_id", "artifact_version"):
        normalized[field] = _require_text(normalized[field], field)

    if normalized["visibility_state"] not in VISIBILITY_STATES:
        raise PublicationAuthorityError("invalid visibility_state")
    if normalized["process_state"] not in PROCESS_STATES:
        raise PublicationAuthorityError("invalid process_state")
    for field in AUTHORITY_FIELDS:
        if not isinstance(normalized[field], bool):
            raise PublicationAuthorityError(f"{field} must be boolean")
    for field in CLAIM_FIELDS:
        if normalized[field] not in {"NONE", "ASSERTED", "AUTHORIZED"}:
            raise PublicationAuthorityError(f"invalid {field} state")

    action = normalized["requested_publication_action"]
    if action not in {"INSPECT", "LIST", "PUBLISH", "ATTRIBUTE", "ASSOCIATE_EXTERNAL"}:
        raise PublicationAuthorityError("invalid requested_publication_action")

    if normalized.get("authority_source") == "VISIBILITY":
        raise PublicationAuthorityError("visibility cannot be an authority source")

    if normalized["process_state"] == "REVIEW_ONLY":
        if any(normalized[field] for field in AUTHORITY_FIELDS):
            raise PublicationAuthorityError("review-only artifacts cannot grant authority")
        if any(normalized[field] != "NONE" for field in CLAIM_FIELDS):
            raise PublicationAuthorityError("review-only artifacts cannot assert external claims")

    references = normalized["external_references"]
    if not isinstance(references, list):
        raise PublicationAuthorityError("external_references must be a list")
    for reference in references:
        if not isinstance(reference, Mapping):
            raise PublicationAuthorityError("external reference must be an object")
        _require_text(reference.get("name"), "external reference name")
        status = reference.get("association_status")
        if status not in {"REFERENCE_ONLY", "REVIEW_REQUESTED", "AUTHORIZED_ASSOCIATION"}:
            raise PublicationAuthorityError("invalid external association_status")
        if status == "AUTHORIZED_ASSOCIATION" and not normalized["public_association_authority"]:
            raise PublicationAuthorityError(
                "authorized external association requires public_association_authority"
            )

    required_authority = {
        "INSPECT": None,
        "LIST": None,
        "PUBLISH": "publication_authority",
        "ATTRIBUTE": "attribution_authority",
        "ASSOCIATE_EXTERNAL": "public_association_authority",
    }[action]
    decision = "ALLOW"
    reason = "non-consequential visibility operation"
    if required_authority and not normalized[required_authority]:
        decision = "DENY"
        reason = f"{required_authority} is not granted"

    body = dict(normalized)
    supplied_hash = body.pop("envelope_sha256", None)
    computed_hash = _hash(body)
    if supplied_hash is not None and supplied_hash != computed_hash:
        raise PublicationAuthorityError("envelope hash mismatch")
    normalized["envelope_sha256"] = computed_hash
    normalized["publisher_decision"] = decision
    normalized["publisher_decision_reason"] = reason
    normalized["visibility_was_authority_source"] = False
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        envelope = json.loads(args.path.read_text(encoding="utf-8"))
        result = validate_envelope(envelope)
    except (OSError, json.JSONDecodeError, PublicationAuthorityError) as exc:
        print(f"DENY: {exc}")
        return 1

    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["publisher_decision"] == "ALLOW" else 2


if __name__ == "__main__":
    raise SystemExit(main())
