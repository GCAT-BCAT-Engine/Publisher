#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

PACKET_PATH = Path("data/autonomy/authoritative-publisher-packet.json")
HANDOFF_PATH = Path("PUBLISHER_MIRROR_HANDOFF.md")
OUT = Path("data/autonomy")
EXPECTED_PLAN_HASH = "bde58a715d87a31844b3b4f7a2f16aba746dcfc24fd175ac007e6ca2400262ee"
EXPECTED_PACKET_HASH = "1a9bec2eeb689e062a21457260fbb455ff8f1cfd16abf054ee59d6faa4504833"
EXPECTED_HANDOFF_MARKER = "This file is the current handoff and task source of truth for `GCAT-BCAT-Engine/Publisher`."


def canonical(value: Mapping[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"JSON root must be object: {path}")
    return value


def main() -> int:
    packet = load_object(PACKET_PATH)
    claimed = packet.get("packet_hash_sha256")
    unsigned = dict(packet)
    unsigned.pop("packet_hash_sha256", None)
    computed = digest(unsigned)
    if claimed != computed or claimed != EXPECTED_PACKET_HASH:
        raise SystemExit("authoritative packet hash mismatch")
    if packet.get("plan_hash_sha256") != EXPECTED_PLAN_HASH:
        raise SystemExit("authoritative plan hash mismatch")
    if packet.get("target_repository") != os.environ.get("GITHUB_REPOSITORY", "GCAT-BCAT-Engine/Publisher"):
        raise SystemExit("target repository mismatch")
    if packet.get("sequence") != 1:
        raise SystemExit("Publisher requires sequence 1")
    if packet.get("transport_is_authority") is not False:
        raise SystemExit("transport authority boundary violated")
    if not HANDOFF_PATH.exists() or EXPECTED_HANDOFF_MARKER not in HANDOFF_PATH.read_text(encoding="utf-8"):
        raise SystemExit("Publisher handoff source marker missing")

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
        "validation": "RETAINED_AUTHORITATIVE_PACKET_INDEPENDENTLY_VALIDATED",
        "publication_authorized": False,
        "release_authorized": False,
        "custody_recorded": False,
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
