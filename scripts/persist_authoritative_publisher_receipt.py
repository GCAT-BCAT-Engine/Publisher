#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

PACKET_PATH = Path("data/autonomy/authoritative-publisher-packet.json")
HANDOFF_PATH = Path("PUBLISHER_MIRROR_HANDOFF.md")
OUT = Path("data/autonomy")
EXPECTED_PACKET_HASH = "1a9bec2eeb689e062a21457260fbb455ff8f1cfd16abf054ee59d6faa4504833"
EXPECTED_PLAN_HASH = "bde58a715d87a31844b3b4f7a2f16aba746dcfc24fd175ac007e6ca2400262ee"
EXPECTED_MARKER = "Publisher now owns the no-manual-action bootstrap"


def canonical(value: Mapping[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"JSON root must be an object: {path}")
    return value


def main() -> int:
    packet = load_object(PACKET_PATH)
    unsigned = dict(packet)
    claimed = unsigned.pop("packet_hash_sha256", None)
    if claimed != EXPECTED_PACKET_HASH or claimed != digest(unsigned):
        raise SystemExit("authoritative Publisher packet hash mismatch")
    if packet.get("plan_hash_sha256") != EXPECTED_PLAN_HASH:
        raise SystemExit("authoritative plan hash mismatch")
    if packet.get("target_repository") != "GCAT-BCAT-Engine/Publisher" or packet.get("sequence") != 1:
        raise SystemExit("Publisher packet target or sequence mismatch")
    if packet.get("transport_is_authority") is not False:
        raise SystemExit("transport authority boundary violated")
    if EXPECTED_MARKER not in HANDOFF_PATH.read_text(encoding="utf-8"):
        raise SystemExit("Publisher handoff marker not satisfied")

    receipt = {
        "artifact_type": "stegverse_adjacent_construction_receipt",
        "completed_utc": utc_now(),
        "construction_profile": packet["construction_profile"],
        "goal_id": packet["goal_id"],
        "packet_hash_sha256": claimed,
        "participants": packet["participants"],
        "plan_hash_sha256": packet["plan_hash_sha256"],
        "result": "COMPLETE",
        "target_repository": packet["target_repository"],
        "target_goal": packet["target_goal"],
        "transport_is_authority": False,
        "validation": "PUBLISHER_WORKFLOW_VALIDATED_AUTHORITATIVE_PACKET",
        "publication_authorized": False,
        "release_authorized": False,
        "custody_recorded": False,
        "deployment_authorized": False,
        "payment_authorized": False,
        "entitlement_authorized": False,
        "execution_authorized": False,
        "manual_user_action_required": False,
    }
    status = {
        "artifact_type": "stegverse_adjacent_construction_target_status",
        "goal_id": packet["goal_id"],
        "result": "COMPLETE",
        "target_repository": packet["target_repository"],
        "packet_hash_sha256": claimed,
        "plan_hash_sha256": packet["plan_hash_sha256"],
        "site_transport_state": "REPOSITORY_OWNED_FOLLOW_ON",
        "transport_is_authority": False,
        "manual_user_action_required": False,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "adjacent-construction-receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "adjacent-construction-status.json").write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("PUBLISHER ADJACENT CONSTRUCTION: COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
