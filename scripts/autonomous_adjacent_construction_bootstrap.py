#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

API = "https://api.github.com"
SOURCE_REPO = "StegVerse-Labs/StegOps-Orchestrator"
PLAN_PATH = "autonomy/adjacent-construction-plan.json"
OUT = Path("data/autonomy")
EVENT_TYPE = "stegverse-adjacent-construction"


def canonical(value: Mapping[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def headers(token: str) -> dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Publisher-autonomous-adjacent-construction",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def api_json(method: str, url: str, token: str, body: Mapping[str, Any] | None = None) -> dict[str, Any] | None:
    request = urllib.request.Request(
        url,
        data=canonical(body) if body is not None else None,
        method=method,
        headers=headers(token),
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
            if not raw:
                return None
            value = json.loads(raw.decode("utf-8"))
            return value if isinstance(value, dict) else None
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"GitHub API {method} {url} failed with HTTP {exc.code}: {detail}") from exc


def contents_url(repository: str, path: str) -> str:
    encoded = "/".join(urllib.parse.quote(part, safe="") for part in path.split("/"))
    return f"{API}/repos/{repository}/contents/{encoded}"


def remote_text(repository: str, path: str, token: str) -> tuple[str, str] | None:
    value = api_json("GET", contents_url(repository, path), token)
    if not value:
        return None
    encoded = str(value.get("content") or "").replace("\n", "")
    return base64.b64decode(encoded).decode("utf-8"), str(value.get("sha") or "")


def put_text(repository: str, path: str, text: str, token: str, message: str) -> None:
    current = remote_text(repository, path, token)
    body: dict[str, Any] = {
        "message": message,
        "content": base64.b64encode(text.encode("utf-8")).decode("ascii"),
    }
    if current:
        if current[0] == text:
            return
        body["sha"] = current[1]
    if api_json("PUT", contents_url(repository, path), token, body) is None:
        raise SystemExit(f"write returned no result: {repository}/{path}")


def load_plan(token: str) -> dict[str, Any]:
    remote = remote_text(SOURCE_REPO, PLAN_PATH, token)
    if not remote:
        raise SystemExit("source construction plan unavailable")
    value = json.loads(remote[0])
    if not isinstance(value, dict):
        raise SystemExit("construction plan root must be an object")
    return value


def target(plan: Mapping[str, Any], sequence: int) -> dict[str, Any]:
    for candidate in plan.get("targets") or []:
        if int(candidate.get("sequence", 0)) == sequence:
            return dict(candidate)
    raise SystemExit(f"missing target sequence {sequence}")


def build_packet(plan: Mapping[str, Any], selected: Mapping[str, Any]) -> dict[str, Any]:
    packet = {
        "artifact_type": "stegverse_adjacent_construction_packet",
        "schema_version": 1,
        "goal_id": plan["goal_id"],
        "generated_utc": utc_now(),
        "participants": list(plan["participants"]),
        "plan_hash_sha256": digest(plan),
        "sequence": int(selected["sequence"]),
        "target_repository": selected["repository"],
        "target_goal": selected["goal"],
        "target_handoff_path": selected["handoff_path"],
        "target_completion_receipt": selected["completion_receipt"],
        "authority_posture": selected["authority_posture"],
        "construction_profile": plan["construction_profile"],
        "transport_is_authority": False,
        "required_target_result": "COMPLETE",
    }
    packet["packet_hash_sha256"] = digest(packet)
    return packet


def valid_receipt(receipt: Mapping[str, Any], plan: Mapping[str, Any], selected: Mapping[str, Any]) -> bool:
    return (
        receipt.get("artifact_type") == "stegverse_adjacent_construction_receipt"
        and receipt.get("goal_id") == plan.get("goal_id")
        and receipt.get("plan_hash_sha256") == digest(plan)
        and receipt.get("participants") == plan.get("participants")
        and receipt.get("target_repository") == selected.get("repository")
        and receipt.get("result") == "COMPLETE"
        and receipt.get("transport_is_authority") is False
        and isinstance(receipt.get("packet_hash_sha256"), str)
    )


def write_local_receipt(plan: Mapping[str, Any], selected: Mapping[str, Any], packet: Mapping[str, Any]) -> None:
    receipt = {
        "artifact_type": "stegverse_adjacent_construction_receipt",
        "completed_utc": utc_now(),
        "construction_profile": packet["construction_profile"],
        "goal_id": packet["goal_id"],
        "packet_hash_sha256": packet["packet_hash_sha256"],
        "participants": packet["participants"],
        "plan_hash_sha256": packet["plan_hash_sha256"],
        "result": "COMPLETE",
        "target_repository": selected["repository"],
        "target_goal": selected["goal"],
        "transport_is_authority": False,
        "validation": "PUBLISHER_OWNED_BOOTSTRAP_PACKET_VALIDATED",
        "publication_authorized": False,
        "release_authorized": False,
        "custody_recorded": False,
        "execution_authorized": False,
        "manual_user_action_required": False,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "adjacent-construction-receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    (OUT / "adjacent-construction-status.json").write_text(json.dumps({
        "artifact_type": "stegverse_adjacent_construction_target_status",
        "goal_id": packet["goal_id"],
        "result": "COMPLETE",
        "target_repository": selected["repository"],
        "transport_is_authority": False,
        "manual_user_action_required": False,
    }, indent=2, sort_keys=True) + "\n")


def site_script() -> str:
    return '''#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
OUT = Path("data/autonomy")
def canonical(value: Mapping[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
def digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()
def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
def main() -> int:
    payload = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    client = payload.get("client_payload") or {}
    packet = client.get("packet")
    if not isinstance(packet, dict): raise SystemExit("missing construction packet")
    if client.get("transport_is_authority") is not False: raise SystemExit("transport authority boundary violated")
    if packet.get("target_repository") != os.environ["GITHUB_REPOSITORY"]: raise SystemExit("packet target mismatch")
    claimed = packet.get("packet_hash_sha256")
    unsigned = dict(packet); unsigned.pop("packet_hash_sha256", None)
    if claimed != digest(unsigned): raise SystemExit("packet hash mismatch")
    if packet.get("transport_is_authority") is not False: raise SystemExit("packet authority boundary violated")
    receipt = {
      "artifact_type":"stegverse_adjacent_construction_receipt","completed_utc":utc_now(),
      "construction_profile":packet.get("construction_profile"),"goal_id":packet["goal_id"],
      "packet_hash_sha256":claimed,"participants":packet["participants"],
      "plan_hash_sha256":packet["plan_hash_sha256"],"result":"COMPLETE",
      "target_repository":packet["target_repository"],"target_goal":packet["target_goal"],
      "transport_is_authority":False,"validation":"SITE_OWNED_PACKET_VALIDATED",
      "publication_authorized":False,"deployment_authorized":False,"release_authorized":False,
      "execution_authorized":False,"manual_user_action_required":False}
    status = {"artifact_type":"stegverse_adjacent_construction_target_status","goal_id":packet["goal_id"],
      "result":"COMPLETE","target_repository":packet["target_repository"],
      "transport_is_authority":False,"manual_user_action_required":False}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/"adjacent-construction-receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\\n")
    (OUT/"adjacent-construction-status.json").write_text(json.dumps(status,indent=2,sort_keys=True)+"\\n")
    print("ADJACENT CONSTRUCTION TARGET: COMPLETE")
    return 0
if __name__ == "__main__": raise SystemExit(main())
'''


def site_workflow() -> str:
    return '''name: Adjacent Construction Intake
on:
  repository_dispatch:
    types: [stegverse-adjacent-construction]
permissions:
  contents: write
concurrency:
  group: adjacent-construction-intake
  cancel-in-progress: false
jobs:
  validate-and-receipt:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python scripts/consume_adjacent_construction_packet.py
      - uses: actions/upload-artifact@v4
        with:
          name: adjacent-construction-target-receipt
          path: data/autonomy/
          if-no-files-found: error
      - name: Persist target-owned receipt
        run: |
          if git diff --quiet -- data/autonomy; then exit 0; fi
          git config user.name "stegverse-automation"
          git config user.email "actions@users.noreply.github.com"
          git add data/autonomy
          git commit -m "chore: persist adjacent construction receipt [adjacent-target-output]"
          git push
'''


def main() -> int:
    token = os.environ.get("AUTONOMY_TRANSPORT_TOKEN", "").strip()
    if not token:
        raise SystemExit("governed transport token unavailable")
    plan = load_plan(token)
    publisher = target(plan, 1)
    if publisher["repository"] != os.environ.get("GITHUB_REPOSITORY"):
        raise SystemExit("Publisher target mismatch")
    handoff = Path(str(publisher["handoff_path"]))
    if not handoff.exists() or str(publisher["required_handoff_marker"]) not in handoff.read_text(encoding="utf-8"):
        raise SystemExit("Publisher handoff marker not satisfied")
    publisher_packet = build_packet(plan, publisher)
    write_local_receipt(plan, publisher, publisher_packet)
    local_receipt = json.loads((OUT / "adjacent-construction-receipt.json").read_text())
    if not valid_receipt(local_receipt, plan, publisher):
        raise SystemExit("Publisher receipt failed self-validation")

    site = target(plan, 2)
    remote_handoff = remote_text(site["repository"], site["handoff_path"], token)
    if not remote_handoff or str(site["required_handoff_marker"]) not in remote_handoff[0]:
        raise SystemExit("Site handoff marker not satisfied")
    put_text(site["repository"], "scripts/consume_adjacent_construction_packet.py", site_script(), token,
             "feat: install bounded adjacent construction intake")
    put_text(site["repository"], ".github/workflows/adjacent-construction-intake.yml", site_workflow(), token,
             "feat: install adjacent construction receipt workflow")
    site_packet = build_packet(plan, site)
    dispatch = {"event_type": EVENT_TYPE, "client_payload": {"packet": site_packet, "transport_is_authority": False}}
    result = api_json("POST", f"{API}/repos/{site['repository']}/dispatches", token, dispatch)
    if result is not None:
        raise SystemExit("Site repository dispatch returned unexpected body")
    print("PUBLISHER AUTONOMOUS BOOTSTRAP: COMPLETE; SITE DISPATCHED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
