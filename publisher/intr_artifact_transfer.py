"""Universal InTr destination adapter for governed Publisher document transfer."""
from __future__ import annotations

import base64
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from publisher.document_pipeline import render_document_bundle, verify_artifact_manifest
from publisher.evaluator_asset_attachment import parse_assets, attach_originals, verify_source_evidence_coverage, digest as asset_manifest_digest

TRANSFER_SCHEMA = "stegverse.publisher.artifact-transfer/v1"
RETURN_SCHEMA = "stegverse.publisher.artifact-return/v1"
MIR_ROUNDTRIP_BINDING_PROFILE = "stegverse.publisher.mir-roundtrip-binding/v1"
SDK_COMPLETION_CAPSULE_PROFILE = "stegverse.sdk.downstream-completion-capsule/v1"
TRANSFER_FIELDS = {
    "schema", "transfer_id", "operation", "export_bundle", "export_sha256",
    "requested_formats", "authorization_ref", "publication_authorized",
    "release_authorized", "execution_authorized", "authority_effect",
}
OPTIONAL_TRANSFER_FIELDS = {"roundtrip_binding", "evaluator_assets"}
BOUNDARY_FALSE_FLAGS = ("publication_authorized", "release_authorized", "execution_authorized")
POST_PUBLISHER_FALSE_FLAGS = (
    "sdk_return_binding_observed",
    "final_stegverse_side_egress_transition_observed",
    "interlock_intr_egress_observed",
    "far_side_transition_observed",
    "authentic_external_mir_endpoint_substitution_observed",
    "communication_complete",
)


class PublisherArtifactTransferError(ValueError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def sha256_value(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise PublisherArtifactTransferError(f"{label} must be an object")
    return copy.deepcopy(dict(value))


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PublisherArtifactTransferError(f"{label} is required")
    return value.strip()


def _normalize_sha256(value: Any, label: str) -> str:
    text = _require_text(value, label).lower()
    if text.startswith("sha256:"):
        text = text[7:]
    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text):
        raise PublisherArtifactTransferError(f"{label} must be a sha256 digest")
    return text


def _validate_no_authority(value: Mapping[str, Any], label: str) -> None:
    if any(value.get(k) is not False for k in BOUNDARY_FALSE_FLAGS):
        raise PublisherArtifactTransferError(f"{label} attempts authority expansion")
    if value.get("authority_effect") != "NONE":
        raise PublisherArtifactTransferError(f"{label} authority effect invalid")


def _validate_sdk_completion_capsule(capsule: Mapping[str, Any]) -> dict[str, Any]:
    value = _require_mapping(capsule, "SDK downstream completion capsule")
    if value.get("profile") != SDK_COMPLETION_CAPSULE_PROFILE:
        raise PublisherArtifactTransferError("SDK downstream completion capsule profile invalid")
    if value.get("authority_effect") != "NONE":
        raise PublisherArtifactTransferError("SDK downstream completion capsule authority effect invalid")
    manifest_hash = _normalize_sha256(value.get("manifest_hash"), "SDK capsule manifest_hash")
    completion_hash = _normalize_sha256(value.get("completion_hash"), "SDK capsule completion_hash")
    response_to = _require_text(value.get("response_to"), "SDK capsule response_to")
    retained_packet_sha256 = _normalize_sha256(value.get("retained_packet_sha256"), "SDK capsule retained_packet_sha256")
    completion = _require_mapping(value.get("completion"), "SDK capsule completion")
    if _normalize_sha256(sha256_value(completion), "computed completion_hash") != completion_hash:
        raise PublisherArtifactTransferError("SDK capsule completion hash mismatch")
    declarations = _require_mapping(value.get("declarations"), "SDK capsule declarations")
    if declarations.get("publisher_required") is not True:
        raise PublisherArtifactTransferError("SDK capsule does not require Publisher")
    if declarations.get("interlock_intr_egress_required") is not True:
        raise PublisherArtifactTransferError("SDK capsule Interlock/InTr egress declaration missing")
    if declarations.get("far_side_transition_required") is not True:
        raise PublisherArtifactTransferError("SDK capsule far-side transition declaration missing")
    return {
        "profile": SDK_COMPLETION_CAPSULE_PROFILE,
        "manifest_hash": manifest_hash,
        "completion_hash": completion_hash,
        "response_to": response_to,
        "retained_packet_sha256": retained_packet_sha256,
        "completion": completion,
        "declarations": declarations,
        "authority_effect": "NONE",
    }


def _validate_roundtrip_binding(binding: Mapping[str, Any], *, publisher_observed: bool) -> dict[str, Any]:
    value = _require_mapping(binding, "roundtrip_binding")
    if value.get("profile") != MIR_ROUNDTRIP_BINDING_PROFILE:
        raise PublisherArtifactTransferError("MIR round-trip binding profile invalid")
    if value.get("goal_task_id") != "MIR-CONNECTION-ROUNDTRIP-TECHNICAL-GUIDE-001":
        raise PublisherArtifactTransferError("MIR round-trip goal binding invalid")
    if str(value.get("cosv_id")) != "50000000100000":
        raise PublisherArtifactTransferError("MIR round-trip COSV binding invalid")
    if value.get("publisher_transition") != "PUBLISHER_ARTIFACT_RETURN_PRODUCED":
        raise PublisherArtifactTransferError("Publisher transition declaration invalid")
    if value.get("publisher_transition_observed") is not publisher_observed:
        raise PublisherArtifactTransferError("Publisher transition observed state invalid")
    if value.get("authority_effect") != "NONE":
        raise PublisherArtifactTransferError("MIR round-trip binding authority effect invalid")
    for field in POST_PUBLISHER_FALSE_FLAGS:
        if value.get(field) is not False:
            raise PublisherArtifactTransferError(f"{field} must remain false")
    capsule = _validate_sdk_completion_capsule(_require_mapping(value.get("downstream_completion_capsule"), "downstream_completion_capsule"))
    manifest_hash = _normalize_sha256(value.get("manifest_hash"), "MIR binding manifest_hash")
    completion_hash = _normalize_sha256(value.get("completion_hash"), "MIR binding completion_hash")
    response_to = _require_text(value.get("response_to"), "MIR binding response_to")
    retained_packet_sha256 = _normalize_sha256(value.get("retained_packet_sha256"), "MIR binding retained_packet_sha256")
    if manifest_hash != capsule["manifest_hash"]:
        raise PublisherArtifactTransferError("MIR binding manifest hash mismatch")
    if completion_hash != capsule["completion_hash"]:
        raise PublisherArtifactTransferError("MIR binding completion hash mismatch")
    if response_to != capsule["response_to"]:
        raise PublisherArtifactTransferError("MIR binding response_to mismatch")
    if retained_packet_sha256 != capsule["retained_packet_sha256"]:
        raise PublisherArtifactTransferError("MIR binding retained packet hash mismatch")
    sdk_state = _require_mapping(value.get("sdk_processor_state"), "sdk_processor_state")
    if sdk_state.get("state") != "SDK_MANIFEST_SELECTED_PROCESSING_EXECUTED":
        raise PublisherArtifactTransferError("SDK processor state invalid")
    if sdk_state.get("processor_result_observed") is not True:
        raise PublisherArtifactTransferError("SDK processor result must be observed")
    result = {
        "profile": MIR_ROUNDTRIP_BINDING_PROFILE,
        "goal_task_id": "MIR-CONNECTION-ROUNDTRIP-TECHNICAL-GUIDE-001",
        "cosv_id": "50000000100000",
        "publisher_transition": "PUBLISHER_ARTIFACT_RETURN_PRODUCED",
        "manifest_hash": manifest_hash,
        "completion_hash": completion_hash,
        "response_to": response_to,
        "retained_packet_sha256": retained_packet_sha256,
        "downstream_completion_capsule": capsule,
        "sdk_processor_state": sdk_state,
        "publisher_transition_observed": publisher_observed,
        "sdk_return_binding_observed": False,
        "final_stegverse_side_egress_transition_observed": False,
        "interlock_intr_egress_observed": False,
        "far_side_transition_observed": False,
        "authentic_external_mir_endpoint_substitution_observed": False,
        "communication_complete": False,
        "authority_effect": "NONE",
    }
    for optional in (
        "publisher_return_schema", "publisher_return_source_export_id", "publisher_return_source_export_sha256",
        "publisher_return_generation_id", "publisher_artifact_manifest_sha256",
    ):
        if optional in value:
            result[optional] = value[optional]
    return result


def _extract_roundtrip_binding(payload: Mapping[str, Any]) -> dict[str, Any] | None:
    if "roundtrip_binding" not in payload:
        return None
    return _validate_roundtrip_binding(_require_mapping(payload.get("roundtrip_binding"), "roundtrip_binding"), publisher_observed=False)


def validate_transfer_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise PublisherArtifactTransferError("artifact transfer field set invalid")
    keys = set(payload)
    if not (TRANSFER_FIELDS.issubset(keys) and keys.issubset(TRANSFER_FIELDS | OPTIONAL_TRANSFER_FIELDS)):
        raise PublisherArtifactTransferError("artifact transfer field set invalid")
    if payload.get("schema") != TRANSFER_SCHEMA or payload.get("operation") != "TRANSFER":
        raise PublisherArtifactTransferError("artifact transfer schema/operation invalid")
    transfer_id = payload.get("transfer_id")
    if not isinstance(transfer_id, str) or not transfer_id:
        raise PublisherArtifactTransferError("transfer_id required")
    _validate_no_authority(payload, "artifact transfer")
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
    binding = _extract_roundtrip_binding(payload)
    if "evaluator_assets" in payload:
        parse_assets(payload["evaluator_assets"])
    if bundle.get("schema_version") == "stegverse.publisher.evidence-report-package/v1":
        verify_source_evidence_coverage(bundle, payload.get("evaluator_assets"))
    result = copy.deepcopy(bundle)
    if binding is not None:
        result["roundtrip_binding"] = binding
    if "evaluator_assets" in payload:
        result["evaluator_assets"] = copy.deepcopy(payload["evaluator_assets"])
    return result


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
    roundtrip_binding = bundle.pop("roundtrip_binding", None)
    evaluator_assets = bundle.pop("evaluator_assets", None)
    out = Path(output_dir)
    manifest, receipt = render_document_bundle(bundle, out)
    if evaluator_assets is not None:
        attach_originals(supplied_assets=evaluator_assets, output_dir=out, manifest=manifest, receipt=receipt)
    if verify_artifact_manifest(out, manifest) is not True:
        raise PublisherArtifactTransferError("rendered artifact manifest failed verification")
    artifacts = []
    for item in manifest["artifacts"]:
        value = (out / item["path"]).read_bytes()
        if sha256_bytes(value) != item["sha256"] or len(value) != item["bytes"]:
            raise PublisherArtifactTransferError("artifact exact-byte verification failed")
        artifacts.append({
            "format": item["format"], "path": item["path"], "sha256": item["sha256"],
            "bytes": item["bytes"], "content_base64": base64.b64encode(value).decode("ascii"),
            **({"media_type": item["media_type"], "source_class": item["source_class"]}
                if item["format"] == "source-original" else {}),
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
    if roundtrip_binding is not None:
        result["roundtrip_binding"] = {
            **roundtrip_binding,
            "publisher_transition_observed": True,
            "publisher_return_schema": RETURN_SCHEMA,
            "publisher_return_source_export_id": bundle["export_id"],
            "publisher_return_source_export_sha256": bundle["export_sha256"],
            "publisher_return_generation_id": receipt["generation_id"],
            "publisher_artifact_manifest_sha256": manifest["manifest_sha256"],
            "sdk_return_binding_observed": False,
            "final_stegverse_side_egress_transition_observed": False,
            "interlock_intr_egress_observed": False,
            "far_side_transition_observed": False,
            "authentic_external_mir_endpoint_substitution_observed": False,
            "communication_complete": False,
            "authority_effect": "NONE",
        }
    return result, canonical_json(result).encode("utf-8")


def verify_artifact_return(return_bytes: bytes) -> dict[str, Any]:
    try:
        value = json.loads(return_bytes.decode("utf-8"))
    except Exception as exc:
        raise PublisherArtifactTransferError("artifact return JSON invalid") from exc
    if value.get("schema") != RETURN_SCHEMA:
        raise PublisherArtifactTransferError("artifact return boundary invalid")
    _validate_no_authority(value, "artifact return")
    manifest = value.get("manifest")
    if not isinstance(manifest, dict):
        raise PublisherArtifactTransferError("artifact return manifest missing")
    if manifest.get("manifest_sha256") != asset_manifest_digest(
        {k: v for k, v in manifest.items() if k != "manifest_sha256"}
    ):
        raise PublisherArtifactTransferError("Publisher artifact manifest digest mismatch")
    receipt = value.get("rendering_receipt")
    if not isinstance(receipt, dict) or receipt.get("manifest_sha256") != manifest["manifest_sha256"]:
        raise PublisherArtifactTransferError("Publisher rendering receipt manifest mismatch")
    if receipt.get("receipt_sha256") != asset_manifest_digest(
        {k: v for k, v in receipt.items() if k != "receipt_sha256"}
    ):
        raise PublisherArtifactTransferError("Publisher rendering receipt digest mismatch")
    rows = manifest.get("artifacts", [])
    returned = value.get("artifacts", [])
    if not isinstance(rows, list) or not isinstance(returned, list):
        raise PublisherArtifactTransferError("Publisher artifact list invalid")
    names = [row.get("path") for row in rows if isinstance(row, dict)]
    returned_names = [row.get("path") for row in returned if isinstance(row, dict)]
    if len(names) != len(set(names)) or len(returned_names) != len(set(returned_names)) or set(names) != set(returned_names):
        raise PublisherArtifactTransferError("Publisher exact source artifact coverage mismatch")
    by_path = {item.get("path"): item for item in rows}
    for item in returned:
        raw = base64.b64decode(item["content_base64"], validate=True)
        if sha256_bytes(raw) != item.get("sha256") or len(raw) != item.get("bytes"):
            raise PublisherArtifactTransferError("artifact return bytes mismatch")
        matching = by_path.get(item.get("path"), {})
        if (matching.get("sha256") != item.get("sha256")
            or matching.get("bytes") != item.get("bytes")
            or matching.get("format") != item.get("format")):
            raise PublisherArtifactTransferError("artifact return manifest binding mismatch")
        if matching.get("format") == "source-original":
            if (item.get("media_type") != matching.get("media_type")
                or item.get("source_class") != matching.get("source_class")):
                raise PublisherArtifactTransferError("exact original media/provenance mismatch")
    if "roundtrip_binding" in value:
        binding = _validate_roundtrip_binding(_require_mapping(value.get("roundtrip_binding"), "return roundtrip_binding"), publisher_observed=True)
        if binding.get("publisher_return_schema") != RETURN_SCHEMA:
            raise PublisherArtifactTransferError("Publisher return schema binding mismatch")
        if binding.get("publisher_return_source_export_id") != value.get("source_export_id"):
            raise PublisherArtifactTransferError("Publisher source export id binding mismatch")
        if binding.get("publisher_return_source_export_sha256") != value.get("source_export_sha256"):
            raise PublisherArtifactTransferError("Publisher source export hash binding mismatch")
        if binding.get("publisher_return_generation_id") != value.get("generation_id"):
            raise PublisherArtifactTransferError("Publisher generation binding mismatch")
        if binding.get("publisher_artifact_manifest_sha256") != manifest.get("manifest_sha256"):
            raise PublisherArtifactTransferError("Publisher artifact manifest binding mismatch")
    if canonical_json(value).encode("utf-8") != return_bytes:
        raise PublisherArtifactTransferError("artifact return bytes are not canonical JSON")
    return value
