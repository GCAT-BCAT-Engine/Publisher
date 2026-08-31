#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
idx=json.loads((ROOT/"data/cosv/task-vector-index.json").read_text())
state=json.loads((ROOT/"data/publisher-orchestration-state.json").read_text())
blocked={x["task_id"]:x for x in state["blocked_tasks"]}
assert idx["profile"]=="task.v1" and idx["width"]==14 and idx["authority_effect"]=="NONE"
for row in idx["tasks"]:
    assert row["binding_mode"]=="EXTERNAL_PROJECTION_READ_ONLY"
    rec=json.loads((ROOT/row["vector_ref"]).read_text())
    src=blocked[row["task_id"]]
    m=rec["exact_metrics"]
    assert rec["vector"]==row["vector"]
    assert m["lifecycle"]=="BLOCKED"
    assert m["canonical_owner_installed"] is True
    assert m["evidence_complete"] is False
    assert m["activated"] is False and m["propagated"] is False
    expected_blockers=len(src["blocked_by"]) if "blocked_by" in src else 1
    assert m["blocker_count"]==expected_blockers
    assert rec["authority_effect"]=="NONE"
assert idx["coverage"]["active_machine_blocked_tasks_projected"]==2
assert idx["coverage"]["active_machine_blocked_tasks_gap"]==0
assert idx["coverage"]["repository_vector_present_claimed"] is False
print("PUBLISHER_COSV_PROJECTION_PASS tasks=2 repository_vector_present=false")
