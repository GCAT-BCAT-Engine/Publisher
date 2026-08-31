"""Universal InTr destination adapter for governed Publisher document transfer."""
from __future__ import annotations

import base64
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from publisher.document_pipeline import render_document_bundle, verify_artifact_manifest

TRANSFER_SCHEMA = "stegverse.publisher.artifact-transfer/v1"
RETURN_SCHEMA = "stegverse.publisher.artifact-return/v1"
TRANSFER_FIELDS = {
    "schema","transfer_id","operation","export_bundle","export_sha256",
    "requested_formats","authorization_ref","publication_authorized",
    "release_authorized","execution_authorized","authority_effect",
}

class PublisherArtifactTransferError(ValueError):
    pass

def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()

def sha256_value(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))

def validate_transfer_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping) or set(payload) != TRANSFER_FIELDS:
        raise PublisherArtifactTransferError("artifact transfer field set invalid")
    if payload.get("schema") != TRANSFER_SCHEMA or payload.get("operation") != "TRANSFER":
        raise PublisherArtifactTransferError("artifact transfer schema/operation invalid")
    transfer_id = payload.get("transfer_id")
    if not isinstance(transfer_id, str) or not transfer_id:
        raise PublisherArtifactTransferError("transfer_id required")
    if any(payload.get(k) is not False for k in ("publication_authorized","release_authorized","execution_authorized")):
        raise PublisherArtifactTransferError("artifact transfer attempts authority expansion")
    if payload.get("authority_effect") != "NONE":
        raise PublisherArtifactTransferError("artifact transfer authority effect invalid")
    bundle = payload.get("export_bundle")
    if not isinstance(bundle, dict):
        raise PublisherArtifactTransferError("export bundle required")
    if payload.get("export_sha256") != bundle.get("export_sha256"):
        raise PublisherArtifactTransferError("export hash binding mismatch")
    if payload.get("requested_formats") != bundle.get("requested_formats"):
        raise PublisherArtifactTransferError("requested format binding mismatch")
    auth = bundle.get("authorization")
    if not isinstance(auth, dict) or payload.get("authorization_ref") != auth.get("authority_ref"):
        raise PublisherArtifactTransferError("authorization binding mismatch")
    return copy.deepcopy(bundle)

def parse_transfer_bytes(payload_bytes: bytes) -> dict[str, Any]:
    if not isinstance(payload_bytes, bytes) or not payload_bytes:
        raise PublisherArtifactTransferError("exact transfer bytes required")
    try:
        parsed = json.loads(payload_bytes.decode("utf-8"))
    except Exception as exc:
        raise PublisherArtifactTransferError("artifact transfer JSON invalid") from exc
    validate_transfer_payload(parsed)
    if canonical_json(parsed).encode("utf-8") != payload_bytes:
        raise PublisherArtifactTransferError("artifact transfer bytes are not canonical JSON")
    return parsed

def process_artifact_transfer(payload_bytes: bytes, output_dir: Path) -> tuple[dict[str, Any], bytes]:
    payload = parse_transfer_bytes(payload_bytes)
    bundle = validate_transfer_payload(payload)
    out = Path(output_dir)
    manifest, receipt = render_document_bundle(bundle, out)
    if verify_artifact_manifest(out, manifest) is not True:
        raise PublisherArtifactTransferError("rendered artifact manifest failed verification")

    artifacts = []
    for item in manifest["artifacts"]:
        value = (out / item["path"]).read_bytes()
        if sha256_bytes(value) != item["sha256"] or len(value) != item["bytes"]:
            raise PublisherArtifactTransferError("artifact exact-byte verification failed")
        artifacts.append({
            "format": item["format"],
            "path": item["path"],
            "sha256": item["sha256"],
            "bytes": item["bytes"],
            "content_base64": base64.b64encode(value).decode("ascii"),
        })

    result = {
        "schema": RETURN_SCHEMA,
        "transfer_id": payload["transfer_id"],
        "source_export_id": bundle["export_id"],
        "source_export_sha256": bundle["export_sha256"],
        "generation_id": receipt["generation_id"],
        "manifest": manifest,
        "rendering_receipt": receipt,
        "artifacts": artifacts,
        "publication_authorized": False,
        "release_authorized": False,
        "execution_authorized": False,
        "authority_effect": "NONE",
    }
    return result, canonical_json(result).encode("utf-8")

def verify_artifact_return(return_bytes: bytes) -> dict[str, Any]:
    try:
        value = json.loads(return_bytes.decode("utf-8"))
    except Exception as exc:
        raise PublisherArtifactTransferError("artifact return JSON invalid") from exc
    if value.get("schema") != RETURN_SCHEMA or value.get("authority_effect") != "NONE":
        raise PublisherArtifactTransferError("artifact return boundary invalid")
    if any(value.get(k) is not False for k in ("publication_authorized","release_authorized","execution_authorized")):
        raise PublisherArtifactTransferError("artifact return attempts authority expansion")
    manifest = value.get("manifest")
    if not isinstance(manifest, dict):
        raise PublisherArtifactTransferError("artifact return manifest missing")
    by_path = {item.get("path"): item for item in manifest.get("artifacts", [])}
    for item in value.get("artifacts", []):
        raw = base64.b64decode(item["content_base64"], validate=True)
        if sha256_bytes(raw) != item.get("sha256") or len(raw) != item.get("bytes"):
            raise PublisherArtifactTransferError("artifact return bytes mismatch")
        if by_path.get(item.get("path"), {}).get("sha256") != item.get("sha256"):
            raise PublisherArtifactTransferError("artifact return manifest binding mismatch")
    if canonical_json(value).encode("utf-8") != return_bytes:
        raise PublisherArtifactTransferError("artifact return bytes are not canonical JSON")
    return value
