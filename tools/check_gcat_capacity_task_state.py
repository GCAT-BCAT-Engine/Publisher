#!/usr/bin/env python3
"""Validate GCAT session inventory and validation task state."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "orchestration/gcat-capacity-session-goal-inventory.json"
TASK_STATE = ROOT / "orchestration/gcat-capacity-task-state.json"
ALLOWED_RESULTS = {"COMPLETE", "BLOCKED", "RETRY", "REVIEW_REQUIRED", "FAILED", "CLAIMED", "SUPERSEDED", "MERGED"}
ALLOWED_CLAIMS = {
    "UNCLAIMED",
    "CLAIMED_FOR_IMPLEMENTATION",
    "CLAIMED_FOR_VALIDATION",
    "CLAIMED_FOR_INTEGRATION",
    "MACHINE_OWNED",
    "BLOCKED",
    "COMPLETE",
    "SUPERSEDED",
    "MERGED_INTO_CANONICAL_WORKSTREAM",
}


def require(condition: bool, message: str, failures: List[str]) -> None:
    if not condition:
        failures.append(message)


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def main() -> int:
    failures: List[str] = []
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    task = json.loads(TASK_STATE.read_text(encoding="utf-8"))

    require(inventory.get("schema_version") == "1.0.0", "inventory schema_version mismatch", failures)
    require(task.get("schema_version") == "1.0.0", "task-state schema_version mismatch", failures)
    require(task.get("task_id") == "GCAT-CAP-008", "task_id mismatch", failures)
    require(task.get("state") in {"CLAIMED_FOR_VALIDATION", "MACHINE_OWNED", "COMPLETE"}, "invalid validation ownership state", failures)
    require(task.get("current_result") in ALLOWED_RESULTS, "invalid current_result", failures)
    require(set(task.get("required_states", [])) == ALLOWED_RESULTS, "required state vocabulary mismatch", failures)
    require(task.get("collision_key"), "collision_key missing", failures)
    require(task.get("release_condition"), "release_condition missing", failures)
    require(task.get("next_executable_task"), "next executable task missing", failures)
    require(task.get("archive_condition"), "archive condition missing", failures)

    created = parse_time(task["claim_created_at"])
    expires = parse_time(task["claim_expires_at"])
    require(created.tzinfo is not None and expires.tzinfo is not None, "claim timestamps must be timezone-aware", failures)
    require(expires > created, "claim expiration must follow creation", failures)
    require((expires - created).days <= 14, "claim duration exceeds 14 days", failures)

    if task.get("state") == "MACHINE_OWNED":
        require(task.get("claim_released_at"), "machine-owned state requires claim_released_at", failures)
        require(task.get("evidence", {}).get("workflow_run_id"), "machine-owned state requires workflow evidence", failures)
        require(task.get("validation", {}).get("hosted_workflow") == "passed", "machine-owned state requires passed hosted workflow", failures)
        require(task.get("validation", {}).get("artifact_inspection") == "passed", "machine-owned state requires inspected artifact", failures)

    goals = inventory.get("goals", [])
    require(len(goals) == 8, "inventory must contain exactly eight canonical tasks", failures)
    ids = [item.get("task_id") for item in goals]
    require(len(ids) == len(set(ids)), "duplicate task IDs", failures)
    require("GCAT-CAP-008" in ids, "automation task absent from inventory", failures)
    for item in goals:
        require(item.get("claim_state") in ALLOWED_CLAIMS, f"{item.get('task_id')}: invalid claim state", failures)
        require(item.get("destination"), f"{item.get('task_id')}: destination missing", failures)
        require(item.get("owner"), f"{item.get('task_id')}: owner missing", failures)
        require(item.get("evidence"), f"{item.get('task_id')}: evidence missing", failures)
        require(item.get("next_action"), f"{item.get('task_id')}: next action missing", failures)

    canonical = inventory.get("canonical_continuation", {})
    require(canonical.get("handoff") == "docs/GCAT_CAPACITY_MIRROR_HANDOFF.md", "canonical handoff mismatch", failures)
    require(canonical.get("pull_request") == 5, "canonical PR mismatch", failures)
    require(canonical.get("issue") == 6, "canonical issue mismatch", failures)

    if failures:
        print("GCAT task-state validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("GCAT task-state validation: PASS")
    print(f"- goals={len(goals)}")
    print(f"- owner_state={task['state']}")
    print(f"- result={task['current_result']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
