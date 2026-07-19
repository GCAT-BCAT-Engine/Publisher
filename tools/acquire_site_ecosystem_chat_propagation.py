#!/usr/bin/env python3
"""Acquire Site Ecosystem Chat propagation without granting publication authority."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "ecosystem-chat-site-propagation-status.json"
SOURCE = "https://raw.githubusercontent.com/StegVerse-Labs/Site/main/data/ecosystem-chat-activation-propagation.json"
EXPECTED_DESTINATION = "GCAT-BCAT-Engine/Publisher"


def canonical_hash(value: dict) -> str:
    clean = {k: v for k, v in value.items() if k not in {"canonical_sha256", "canonical_hash"}}
    raw = json.dumps(clean, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    request = Request(SOURCE, headers={"Accept": "application/json", "User-Agent": "Publisher-Site-Propagation-Consumer/1.0"})
    with urlopen(request, timeout=30) as response:
        source = json.loads(response.read().decode("utf-8"))

    if not isinstance(source, dict):
        raise SystemExit("DENY: Site propagation must be a JSON object")

    state = str(source.get("state", "UNKNOWN"))
    destinations = source.get("destinations", source.get("canonical_destinations", []))
    if EXPECTED_DESTINATION not in destinations:
        raise SystemExit("DENY: Publisher is not a declared propagation destination")

    declared_hash = source.get("canonical_sha256") or source.get("canonical_hash")
    computed_hash = canonical_hash(source)
    hash_valid = declared_hash in {None, computed_hash}
    if not hash_valid:
        raise SystemExit("DENY: Site propagation canonical hash mismatch")

    authority = source.get("authority", {})
    forbidden_true = [key for key, value in authority.items() if value is True]
    if forbidden_true:
        raise SystemExit(f"DENY: authority escalation in Site propagation: {forbidden_true}")

    ready = state == "READY_FOR_DOWNSTREAM_INGESTION"
    blockers = source.get("blockers", [])
    if not ready and not blockers:
        blockers = ["site_activation_not_ready_for_downstream_ingestion"]

    payload = {
        "schema_version": "1.0",
        "repository": EXPECTED_DESTINATION,
        "source_repository": "StegVerse-Labs/Site",
        "source_url": SOURCE,
        "observed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_state": state,
        "source_canonical_sha256": computed_hash,
        "source_hash_valid": hash_valid,
        "destination_declared": True,
        "state": "VERIFIED_INGESTION_READY" if ready else "PENDING_SITE_ACTIVATION",
        "blockers": [] if ready else blockers,
        "manual_user_action_required": False,
        "authority": {
            "publication_authority": False,
            "release_authority": False,
            "activation_authority": False,
            "admissibility_authority": False,
            "execution_authority": False
        }
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"state": payload["state"], "source_state": state}))


if __name__ == "__main__":
    main()
