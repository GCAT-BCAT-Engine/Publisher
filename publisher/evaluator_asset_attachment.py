"""Exact original evaluator evidence passthrough on the existing Publisher transfer path.

This is an attachment substage of Publisher's *existing* admitted document
transfer, not a transport, separate renderer, source-of-truth, or custody owner.
Its receipt proves only verified exact bytes included in this Publisher return.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping

from publisher.document_pipeline import verify_artifact_manifest

SAFE_PATH = re.compile(r"^evidence/[A-Za-z0-9][A-Za-z0-9._-]{0,127}\.(?:png|jpg|jpeg|pdf|json|txt|md)$")
MEDIA_TYPES = {"image/png", "image/jpeg", "application/pdf", "application/json", "text/plain", "text/markdown"}
MAX_ONE = 20 * 1024 * 1024
MAX_TOTAL = 80 * 1024 * 1024

class EvaluatorAssetError(ValueError):
    pass

def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()

def digest(value: Any) -> str:
    return sha(canonical_json(value).encode("utf-8"))

def parse_assets(items: Any) -> list[tuple[dict[str, Any], bytes]]:
    if not isinstance(items, list) or not items:
        raise EvaluatorAssetError("evaluator_assets must be a non-empty array when declared")
    parsed: list[tuple[dict[str, Any], bytes]] = []
    seen: set[str] = set()
    total = 0
    for index, item in enumerate(items):
        if not isinstance(item, dict) or set(item) != {
            "path", "media_type", "sha256", "bytes", "content_base64", "source_class"
        }:
            raise EvaluatorAssetError(f"evaluator_assets[{index}] exact fields required")
        path = item["path"]
        if not isinstance(path, str) or not SAFE_PATH.fullmatch(path) or path in seen:
            raise EvaluatorAssetError(f"evaluator_assets[{index}] unsafe/duplicate path")
        seen.add(path)
        media = item["media_type"]
        if media not in MEDIA_TYPES:
            raise EvaluatorAssetError("unsupported evaluator asset media type")
        ext = path.rsplit(".", 1)[-1]
        if (media == "image/png" and ext != "png") or (
            media == "image/jpeg" and ext not in {"jpg", "jpeg"}
        ) or (media == "application/pdf" and ext != "pdf"):
            raise EvaluatorAssetError("asset media type/path mismatch")
        if item["source_class"] not in {"USER_SUPPLIED_ORIGINAL", "AUTHENTIC_RETAINED_EVIDENCE", "COUNTERPART_SUPPLIED_ORIGINAL", "SDK_SOURCE_VALIDATED_ARTIFACT"}:
            raise EvaluatorAssetError("unknown source class")
        try:
            raw = base64.b64decode(item["content_base64"], validate=True)
        except Exception as exc:
            raise EvaluatorAssetError("invalid base64 evidence") from exc
        if not raw or len(raw) > MAX_ONE:
            raise EvaluatorAssetError("invalid single evaluator asset size")
        total += len(raw)
        if total > MAX_TOTAL:
            raise EvaluatorAssetError("evaluator evidence total exceeds size bound")
        if item["bytes"] != len(raw) or item["sha256"] != sha(raw):
            raise EvaluatorAssetError("original evidence hash/size mismatch")
        if media == "image/png" and not raw.startswith(b"\x89PNG\r\n\x1a\n"):
            raise EvaluatorAssetError("claimed PNG signature mismatch")
        if media == "application/pdf" and not raw.startswith(b"%PDF-"):
            raise EvaluatorAssetError("claimed PDF signature mismatch")
        parsed.append((copy.deepcopy(item), raw))
    return parsed

def attach_originals(
    *,
    supplied_assets: Any,
    output_dir: Path,
    manifest: dict[str, Any],
    receipt: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    """Attach originals, rebind existing manifest/receipt; never infer physical truth."""
    parsed = parse_assets(supplied_assets)
    out = Path(output_dir)
    existing_paths = {a["path"] for a in manifest["artifacts"]}
    additions: list[dict[str, Any]] = []
    returned: list[dict[str, Any]] = []
    for item, raw in parsed:
        if item["path"] in existing_paths:
            raise EvaluatorAssetError("asset collides with rendered artifact")
        dest = out / item["path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and dest.read_bytes() != raw:
            raise EvaluatorAssetError("immutable evidence path differs")
        if not dest.exists():
            dest.write_bytes(raw)
        manifest_item = {
            "format": "source-original",
            "media_type": item["media_type"],
            "source_class": item["source_class"],
            "path": item["path"],
            "sha256": item["sha256"],
            "bytes": item["bytes"],
            "validation_state": "EXACT_BYTES_VALIDATED_NOT_INDEPENDENTLY_ATTESTED",
        }
        additions.append(manifest_item)
        returned.append({
            "format": "source-original",
            "path": item["path"],
            "sha256": item["sha256"],
            "bytes": item["bytes"],
            "content_base64": item["content_base64"],
            "media_type": item["media_type"],
            "source_class": item["source_class"],
        })
    manifest["artifacts"].extend(additions)
    manifest["manifest_sha256"] = digest({k:v for k,v in manifest.items() if k != "manifest_sha256"})
    receipt["manifest_sha256"] = manifest["manifest_sha256"]
    receipt["receipt_sha256"] = digest({k:v for k,v in receipt.items() if k != "receipt_sha256"})
    (out / "artifact-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "rendering-receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not verify_artifact_manifest(out, manifest):
        raise EvaluatorAssetError("augmented artifact manifest verification failed")
    return returned, manifest, receipt

def verify_source_evidence_coverage(bundle: Mapping[str, Any], assets: Any) -> None:
    """Require every exact evaluator-original in the claimed report to be supplied."""
    expected = {}
    for row in bundle.get("evidence", []):
        path = row.get("path")
        if not isinstance(path, str) or not path.startswith("evidence/"):
            continue
        if (row.get("fidelity") != "exact" or row.get("payload_available") is not True
            or row.get("restricted") is not False):
            raise EvaluatorAssetError("original source evidence inventory must be exact and available")
        if path in expected:
            raise EvaluatorAssetError("duplicate original evidence inventory path")
        expected[path] = row
    actual = {meta["path"]: meta for meta, _ in parse_assets(assets)} if assets is not None else {}
    if set(expected) != set(actual):
        raise EvaluatorAssetError("original evaluator evidence coverage mismatch")
    for path, item in expected.items():
        asset = actual[path]
        if (item["content_hash"] != asset["sha256"]
            or item.get("bytes") != asset["bytes"]
            or item.get("media_type") != asset["media_type"]):
            raise EvaluatorAssetError("evaluator evidence inventory does not match original bytes")
