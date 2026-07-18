#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

API = "https://api.github.com"
SOURCE_REPO = "StegVerse-Labs/StegOps-Orchestrator"
PLAN_PATH = "autonomy/adjacent-construction-plan.json"
PACKET_PATH = "docs/_automation/adjacent-construction/latest/packet.json"
OUT = Path("data/autonomy")


def canonical(value: Mapping[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def fetch_json(path: str, token: str) -> dict[str, Any]:
    request = urllib.request.Request(
        f"{API}/repos/{SOURCE_REPO}/contents/{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "Publisher-authoritative-adjacent-consumer",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        wrapper = json.loads(response.read().decode("utf-8"))
    value = json.loads(base64.b64decode(str(wrapper["content"]).replace("\n", "")).decode("utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"JSON root must be object: {path}")
    return value


def main() -> int:
    token = os.environ.get("AUTONOMY_TRANSPORT_TOKEN", "").strip()
    if not token:
        raise SystemExit("governed transport token unavailable")
    plan = fetch_json(PLAN_PATH, token)
    packet = fetch_json(PACKET_PATH, token)
    claimed = packet.get("packet_hash_sha256")
    unsigned = dict(packet)
    unsigned.pop("packet_hash_sha256", None)
    if claimed != digest(unsigned):
        raise SystemExit("authoritative packet hash mismatch")
    if packet.get("plan_hash_sha256") != digest(plan):
        raise SystemExit("authoritative plan hash mismatch")
    if packet.get("target_repository") != os.environ.get("GITHUB_REPOSITORY"):
        raise SystemExit("target repository mismatch")
    if packet.get("sequence") != 1:
        raise SystemExit("Publisher requires sequence 1")
    if packet.get("transport_is_authority") is not False:
        raise SystemExit("transport authority boundary violated")
    handoff = Path(str(packet.get("target_handoff_path")))
    expected = "This file is the current handoff and task source of truth for `GCAT-BCAT-Engine/Publisher`."
    if not handoff.exists() or expected not in handoff.read_text(encoding="utf-8"):
        raise SystemExit("Publisher handoff source marker missing")
    receipt = {
        "artifact_type": "stegverse_adjacent_construction_receipt",
        "completed_utc": utc_now(),
        "construction_profile": packet["construction_profile"],
        "goal_id": packet["goal_id"],
        "packet_hash_sha256": packet["packet_hash_sha256"],
        "participants": packet["participants"],
        "plan_hash_sha256": packet["plan_hash_sha256"],
        "result": "COMPLETE",
        "target_repository": packet["target_repository"],
        "target_goal": packet["target_goal"],
        "transport_is_authority": False,
        "validation": "AUTHORITATIVE_SOURCE_PACKET_INDEPENDENTLY_VALIDATED",
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
        "packet_hash_sha256": packet["packet_hash_sha256"],
        "plan_hash_sha256": packet["plan_hash_sha256"],
        "transport_is_authority": False,
        "manual_user_action_required": False,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "adjacent-construction-receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    (OUT / "adjacent-construction-status.json").write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
    print("PUBLISHER ADJACENT CONSTRUCTION: COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
