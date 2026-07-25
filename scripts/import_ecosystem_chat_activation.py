#!/usr/bin/env python3
"""Import verified Ecosystem Chat activation evidence from StegVerse-Labs/Site.

Publisher accepts the projection only after Site activation, propagation, and the
Master-Records custody projection for the Site orchestration terminal receipt are
all hash-valid and mutually bound. This importer grants no publication, release,
custody, execution, or activation authority.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any
from urllib import error, request

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "ecosystem-chat-activation-status.json"
STATE_URL = os.getenv(
    "STEGVERSE_SITE_ECOSYSTEM_CHAT_STATE_URL",
    "https://raw.githubusercontent.com/StegVerse-Labs/Site/main/data/ecosystem-chat-activation-state.json",
)
PACKET_URL = os.getenv(
    "STEGVERSE_SITE_ECOSYSTEM_CHAT_PROPAGATION_URL",
    "https://raw.githubusercontent.com/StegVerse-Labs/Site/main/data/ecosystem-chat-activation-propagation.json",
)
CUSTODY_URL = os.getenv(
    "STEGVERSE_SITE_ORCHESTRATION_CUSTODY_URL",
    "https://raw.githubusercontent.com/StegVerse-Labs/Site/main/data/site-orchestration-terminal-custody.json",
)
TIMEOUT = float(os.getenv("STEGVERSE_SITE_ACTIVATION_FETCH_TIMEOUT_SECONDS", "20"))


def canonical_hash(payload: dict[str, Any], hash_field: str) -> str:
    material = dict(payload)
    material.pop(hash_field, None)
    return hashlib.sha256(
        json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def fetch_json(url: str) -> dict[str, Any]:
    outbound = request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "StegVerse-Publisher-Activation-Importer/2.0"},
    )
    with request.urlopen(outbound, timeout=TIMEOUT) as response:
        value = json.loads(response.read().decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("source_not_object")
    return value


def validate(
    state: dict[str, Any], packet: dict[str, Any], custody: dict[str, Any]
) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if state.get("record_type") != "ecosystem_chat_activation_state":
        failures.append("state_record_type_mismatch")
    if state.get("state_sha256") != canonical_hash(state, "state_sha256"):
        failures.append("state_digest_mismatch")
    if packet.get("schema") != "stegverse.ecosystem_chat.activation_propagation.v1":
        failures.append("packet_schema_mismatch")
    if packet.get("packet_sha256") != canonical_hash(packet, "packet_sha256"):
        failures.append("packet_digest_mismatch")
    if packet.get("source_state_sha256") != state.get("state_sha256"):
        failures.append("packet_state_binding_mismatch")

    if custody.get("schema") != "stegverse.master_records.site_orchestration_terminal_custody.v1":
        failures.append("custody_schema_mismatch")
    if custody.get("custody_sha256") != canonical_hash(custody, "custody_sha256"):
        failures.append("custody_digest_mismatch")
    if custody.get("custody_state") != "RECORDED":
        failures.append("terminal_custody_not_recorded")
    reconstruction = custody.get("reconstruction") or {}
    if reconstruction.get("state") != "PASS":
        failures.append("terminal_reconstruction_not_pass")
    if reconstruction.get("exact_commit_binding") is not True:
        failures.append("terminal_exact_commit_binding_missing")
    if reconstruction.get("stage_chain_complete") is not True:
        failures.append("terminal_stage_chain_incomplete")
    if reconstruction.get("supersession_clear") is not True:
        failures.append("terminal_supersession_not_clear")
    if custody.get("authority_effect") != "NONE":
        failures.append("custody_authority_boundary_invalid")

    packet_custody_sha = packet.get("terminal_custody_sha256")
    state_custody_sha = state.get("terminal_custody_sha256")
    custody_sha = custody.get("custody_sha256")
    if not packet_custody_sha or packet_custody_sha != custody_sha:
        failures.append("packet_custody_binding_mismatch")
    if not state_custody_sha or state_custody_sha != custody_sha:
        failures.append("state_custody_binding_mismatch")

    boundary = packet.get("authority_boundary") or {}
    for key in (
        "propagation_is_activation_authority",
        "propagation_is_release_authority",
        "propagation_is_publication_authority",
        "propagation_is_custody",
    ):
        if boundary.get(key) is not False:
            failures.append(f"authority_boundary_invalid:{key}")

    destinations = packet.get("destinations") or []
    publisher = next(
        (item for item in destinations if item.get("repository") == "GCAT-BCAT-Engine/Publisher"),
        None,
    )
    if publisher is None:
        failures.append("publisher_destination_missing")
    elif publisher.get("manual_user_action_required") is not False:
        failures.append("publisher_manual_action_boundary_invalid")

    ready = (
        not failures
        and state.get("state") == "ACTIVATION_COMPLETE"
        and all((state.get("gates") or {}).values())
        and packet.get("state") == "READY_FOR_DOWNSTREAM_INGESTION"
        and publisher is not None
        and publisher.get("ingestion_ready") is True
    )
    return ready, failures


def write(
    status: str,
    reason: str,
    state: dict[str, Any] | None = None,
    packet: dict[str, Any] | None = None,
    custody: dict[str, Any] | None = None,
) -> None:
    payload: dict[str, Any] = {
        "schema": "stegverse.publisher.ecosystem_chat_activation_status.v2",
        "status": status,
        "reason": reason,
        "source_repository": "StegVerse-Labs/Site",
        "custody_repository": "master-records/orchestration",
        "source_state_sha256": state.get("state_sha256") if state else None,
        "source_packet_sha256": packet.get("packet_sha256") if packet else None,
        "terminal_custody_sha256": custody.get("custody_sha256") if custody else None,
        "activation_complete": status == "VERIFIED_ACTIVATION_IMPORTED",
        "terminal_custody_verified": status == "VERIFIED_ACTIVATION_IMPORTED",
        "publication_authorized": False,
        "release_authorized": False,
        "custody_recorded": False,
        "execution_authorized": False,
        "manual_user_action_required": False,
    }
    payload["status_sha256"] = canonical_hash(payload, "status_sha256")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    try:
        state = fetch_json(STATE_URL)
        packet = fetch_json(PACKET_URL)
        custody = fetch_json(CUSTODY_URL)
    except error.HTTPError as exc:
        write("PENDING_SITE_ACTIVATION", f"source_http_status_{exc.code}")
        return 0
    except (error.URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError) as exc:
        write("PENDING_SITE_ACTIVATION", f"source_unavailable:{type(exc).__name__}")
        return 0

    ready, failures = validate(state, packet, custody)
    if failures:
        write("REJECTED_SITE_ACTIVATION", ";".join(sorted(failures)), state, packet, custody)
        return 1
    if not ready:
        write("PENDING_SITE_ACTIVATION", "site_activation_or_terminal_custody_not_complete", state, packet, custody)
        return 0
    write(
        "VERIFIED_ACTIVATION_IMPORTED",
        "hash_bound_site_activation_propagation_and_terminal_custody_verified",
        state,
        packet,
        custody,
    )
    print("PUBLISHER_ECOSYSTEM_CHAT_ACTIVATION_IMPORT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
