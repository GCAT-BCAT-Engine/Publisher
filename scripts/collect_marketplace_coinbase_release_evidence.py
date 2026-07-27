#!/usr/bin/env python3
"""Collect and verify Marketplace–Coinbase paper evidence across repositories.

This collector is evidence-only. It never grants publication, release, execution,
custody, payment, withdrawal, or live financial authority.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error, request

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "marketplace-coinbase-release-evidence-status.json"
EVIDENCE_DIR = ROOT / "data" / "marketplace-coinbase-release-evidence"
PUBLICATION_DIR = ROOT / "data" / "marketplace-coinbase-publications"
TOKEN = os.getenv("MARKETPLACE_COINBASE_EVIDENCE_TOKEN", "")
API = "https://api.github.com"

SOURCES = {
    "crypto_bot": {
        "repo": "StegVerse-Labs/crypto-bot",
        "artifact": "paper-release-readiness",
        "required": ["PAPER_RELEASE_READINESS.json", "CROSS_REPOSITORY_EVIDENCE.json"],
    },
    "marketplace": {
        "repo": "GCAT-BCAT-Engine/Marketplace",
        "artifact": "marketplace-coinbase-settlement-import",
        "required": [],
    },
}


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value)).hexdigest()


def without(value: dict[str, Any], field: str) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != field}


def api_json(path: str) -> dict[str, Any]:
    req = request.Request(
        API + path,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "User-Agent": "StegVerse-Marketplace-Coinbase-Evidence-Collector/1.2",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with request.urlopen(req, timeout=30) as response:
        value = json.loads(response.read().decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("github_response_not_object")
    return value


def download(url: str) -> bytes:
    req = request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "User-Agent": "StegVerse-Marketplace-Coinbase-Evidence-Collector/1.2",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with request.urlopen(req, timeout=60) as response:
        return response.read()


def latest_artifact(repo: str, artifact_name: str) -> dict[str, Any] | None:
    page = api_json(f"/repos/{repo}/actions/artifacts?per_page=100&name={artifact_name}")
    artifacts = page.get("artifacts") or []
    candidates = [item for item in artifacts if not item.get("expired")]
    candidates.sort(key=lambda item: item.get("created_at") or "", reverse=True)
    return candidates[0] if candidates else None


def find_named(directory: Path, filename: str) -> Path | None:
    matches = sorted(path for path in directory.rglob(filename) if path.is_file())
    return matches[0] if matches else None


def extract_artifact(source_key: str, source: dict[str, Any]) -> dict[str, Any]:
    artifact = latest_artifact(source["repo"], source["artifact"])
    if artifact is None:
        return {"state": "MISSING", "repository": source["repo"], "artifact": source["artifact"]}
    archive = download(str(artifact["archive_download_url"]))
    destination = EVIDENCE_DIR / source_key
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)
    extracted: list[str] = []
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        for member in bundle.namelist():
            if member.endswith("/"):
                continue
            relative = Path(member)
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("unsafe_artifact_path")
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(bundle.read(member))
            extracted.append(relative.as_posix())
    missing = [name for name in source["required"] if find_named(destination, name) is None]
    return {
        "state": "PASS" if not missing else "INVALID",
        "repository": source["repo"],
        "artifact": source["artifact"],
        "artifact_id": artifact.get("id"),
        "workflow_run_id": artifact.get("workflow_run", {}).get("id"),
        "created_at": artifact.get("created_at"),
        "files": sorted(extracted),
        "missing_required_files": missing,
    }


def load_crypto_evidence() -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    directory = EVIDENCE_DIR / "crypto_bot"
    readiness_path = find_named(directory, "PAPER_RELEASE_READINESS.json")
    cross_path = find_named(directory, "CROSS_REPOSITORY_EVIDENCE.json")
    if readiness_path is None or cross_path is None:
        return None, None
    return (
        json.loads(readiness_path.read_text(encoding="utf-8")),
        json.loads(cross_path.read_text(encoding="utf-8")),
    )


def validate_crypto_repository_readiness() -> list[str]:
    """Validate repository CI evidence without requiring ecosystem-final readiness."""
    failures: list[str] = []
    readiness, cross = load_crypto_evidence()
    if readiness is None or cross is None:
        return ["crypto_bot_release_evidence_files_missing"]
    readiness_body = without(readiness, "receipt_digest")
    cross_body = without(cross, "manifest_digest")
    if readiness.get("receipt_digest") != digest(readiness_body):
        failures.append("readiness_receipt_digest_mismatch")
    if cross.get("manifest_digest") != digest(cross_body):
        failures.append("cross_repository_manifest_digest_mismatch")
    if readiness.get("cross_repository_evidence_digest") != cross.get("manifest_digest"):
        failures.append("readiness_cross_repository_binding_mismatch")
    if readiness.get("ci_tests") != "PASS":
        failures.append("crypto_bot_ci_tests_not_pass")
    if readiness.get("paper_runtime") != "IMPLEMENTED":
        failures.append("crypto_bot_paper_runtime_not_implemented")
    if readiness.get("release_decision") not in {
        "PAPER_RELEASE_BLOCKED_PENDING_CROSS_REPOSITORY_EVIDENCE",
        "PAPER_RELEASE_READY",
    }:
        failures.append("unsupported_repository_readiness_decision")
    if readiness.get("live_authority") != "NOT_GRANTED":
        failures.append("live_authority_boundary_invalid")
    if cross.get("live_authority_granted") is not False:
        failures.append("cross_repository_live_authority_boundary_invalid")
    return failures


def marketplace_json_objects() -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    directory = EVIDENCE_DIR / "marketplace"
    for path in sorted(directory.rglob("*.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(value, dict):
            values.append(value)
    return values


def publisher_publication_objects() -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for path in sorted(PUBLICATION_DIR.glob("*.publication.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(value, dict):
            values.append(value)
    return values


def reconstruct_ecosystem_evidence() -> tuple[list[str], dict[str, Any]]:
    failures: list[str] = []
    values = marketplace_json_objects()
    packet = next((item for item in values if item.get("packet_version") == "marketplace-coinbase-settlement-export-v1"), None)
    ack = next((item for item in values if item.get("ack_version") == "marketplace-coinbase-settlement-ack-v1"), None)
    market_transport = next((item for item in values if item.get("transport_version") == "marketplace-coinbase-transport-v1" and item.get("sequence") == 1), None)
    publisher_transport = next((item for item in values if item.get("transport_version") == "marketplace-coinbase-transport-v1" and item.get("sequence") == 2), None)
    missing = [name for name, value in (
        ("settlement_packet", packet),
        ("marketplace_acknowledgement", ack),
        ("marketplace_transport", market_transport),
        ("publisher_transport", publisher_transport),
    ) if value is None]
    if missing:
        return [f"marketplace_artifact_missing:{name}" for name in missing], {}
    assert packet is not None and ack is not None and market_transport is not None and publisher_transport is not None

    publication = next(
        (
            item for item in publisher_publication_objects()
            if (item.get("projection") or {}).get("intent_id") == packet.get("intent_id")
            and item.get("result") in {"ACCEPTED", "DUPLICATE"}
        ),
        None,
    )
    if publication is None:
        return ["publisher_publication_evidence_missing"], {}
    projection = publication.get("projection") or {}
    receipt = publication.get("publication_receipt") or {}

    for value, field, label in (
        (packet, "packet_digest", "settlement_packet"),
        (ack, "ack_digest", "marketplace_acknowledgement"),
        (market_transport, "transport_digest", "marketplace_transport"),
        (publisher_transport, "transport_digest", "publisher_transport"),
        (projection, "projection_digest", "publisher_projection"),
        (receipt, "receipt_digest", "publication_receipt"),
    ):
        if value.get(field) != digest(without(value, field)):
            failures.append(f"{label}_digest_mismatch")

    intent_id = packet.get("intent_id")
    packet_digest = packet.get("packet_digest")
    ack_digest = ack.get("ack_digest")
    market_transport_digest = market_transport.get("transport_digest")
    publisher_transport_digest = publisher_transport.get("transport_digest")
    projection_digest = projection.get("projection_digest")
    bindings = {
        "intent_id": intent_id,
        "packet_digest": packet_digest,
        "marketplace_transport_digest": market_transport_digest,
        "marketplace_ack_digest": ack_digest,
        "publisher_transport_digest": publisher_transport_digest,
        "publisher_projection_digest": projection_digest,
        "publication_receipt_digest": receipt.get("receipt_digest"),
    }

    comparisons = (
        (market_transport.get("intent_id"), intent_id, "marketplace_transport_intent_mismatch"),
        (market_transport.get("packet_digest"), packet_digest, "marketplace_transport_packet_mismatch"),
        (ack.get("intent_id"), intent_id, "marketplace_ack_intent_mismatch"),
        (ack.get("packet_digest"), packet_digest, "marketplace_ack_packet_mismatch"),
        (ack.get("transport_digest"), market_transport_digest, "ack_sequence_1_binding_mismatch"),
        (publisher_transport.get("intent_id"), intent_id, "publisher_transport_intent_mismatch"),
        (publisher_transport.get("packet_digest"), packet_digest, "publisher_transport_packet_mismatch"),
        (publisher_transport.get("previous_transport_digest"), market_transport_digest, "transport_chain_binding_mismatch"),
        (publisher_transport.get("marketplace_ack_digest"), ack_digest, "transport_ack_binding_mismatch"),
        (projection.get("intent_id"), intent_id, "publisher_projection_intent_mismatch"),
        (projection.get("packet_digest"), packet_digest, "publisher_projection_packet_mismatch"),
        (projection.get("marketplace_ack_digest"), ack_digest, "publisher_projection_ack_mismatch"),
        (receipt.get("intent_id"), intent_id, "publication_receipt_intent_mismatch"),
        (receipt.get("projection_digest"), projection_digest, "publication_receipt_projection_mismatch"),
        (receipt.get("transport_digest"), publisher_transport_digest, "publication_receipt_transport_mismatch"),
    )
    for actual, expected, message in comparisons:
        if actual != expected:
            failures.append(message)

    if ack.get("result") not in {"ACCEPTED", "DUPLICATE"} or ack.get("marketplace_indexed") is not True:
        failures.append("marketplace_ack_not_accepted_and_indexed")
    if projection.get("paper_evidence_verified") is not True:
        failures.append("publisher_projection_not_verified")
    if receipt.get("result") not in {"ACCEPTED", "DUPLICATE"}:
        failures.append("publication_receipt_not_accepted")

    for name, value in (
        ("settlement_packet", packet),
        ("marketplace_acknowledgement", ack),
        ("marketplace_transport", market_transport),
        ("publisher_transport", publisher_transport),
        ("publisher_projection", projection),
        ("publication_receipt", receipt),
    ):
        if value.get("live_authority_granted") is not False:
            failures.append(f"{name}_live_authority_boundary_invalid")
    if market_transport.get("transport_is_authority") is not False or publisher_transport.get("transport_is_authority") is not False:
        failures.append("transport_authority_boundary_invalid")
    for field in ("publication_authorized", "release_authorized"):
        if projection.get(field) is not False or receipt.get(field) is not False:
            failures.append(f"publisher_{field}_boundary_invalid")

    _, cross = load_crypto_evidence()
    if cross is not None and cross.get("result") == "PASS":
        if cross.get("evidence_bindings") != bindings:
            failures.append("crypto_manifest_ecosystem_binding_mismatch")
    return failures, bindings


def write(
    status: str,
    reason: str,
    sources: dict[str, Any] | None = None,
    failures: list[str] | None = None,
    bindings: dict[str, Any] | None = None,
) -> None:
    readiness, cross = load_crypto_evidence()
    body = {
        "schema": "stegverse.publisher.marketplace_coinbase_release_evidence.v2",
        "status": status,
        "reason": reason,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "sources": sources or {},
        "failures": sorted(failures or []),
        "evidence_bindings": bindings or {},
        "crypto_repository_readiness_receipt_digest": (readiness or {}).get("receipt_digest"),
        "crypto_repository_manifest_digest": (cross or {}).get("manifest_digest"),
        "paper_release_verified": status == "VERIFIED",
        "publication_authorized": False,
        "release_authorized": False,
        "execution_authorized": False,
        "live_authority_granted": False,
        "manual_user_action_required": False,
    }
    payload = {**body, "status_digest": digest(body)}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    if not TOKEN:
        write("PENDING_CREDENTIAL", "MARKETPLACE_COINBASE_EVIDENCE_TOKEN_not_available")
        print("MARKETPLACE_COINBASE_EVIDENCE_PENDING_CREDENTIAL")
        return 0
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        sources = {key: extract_artifact(key, value) for key, value in SOURCES.items()}
    except (error.HTTPError, error.URLError, TimeoutError, OSError, ValueError, zipfile.BadZipFile) as exc:
        write("PENDING_SOURCE", f"source_collection_failed:{type(exc).__name__}")
        return 0
    source_failures = [f"{key}:{value['state']}" for key, value in sources.items() if value.get("state") != "PASS"]
    validation_failures: list[str] = []
    bindings: dict[str, Any] = {}
    if not source_failures:
        validation_failures.extend(validate_crypto_repository_readiness())
        if not validation_failures:
            ecosystem_failures, bindings = reconstruct_ecosystem_evidence()
            validation_failures.extend(ecosystem_failures)
    failures = source_failures + validation_failures
    if failures:
        write("REJECTED", "cross_repository_release_evidence_not_verified", sources, failures, bindings)
        return 1
    write("VERIFIED", "publisher_reconstructed_hash_bound_paper_release_evidence", sources, bindings=bindings)
    print("MARKETPLACE_COINBASE_RELEASE_EVIDENCE_VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
