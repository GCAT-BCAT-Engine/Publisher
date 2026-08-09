#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "correctability-projection.json"

EXPECTED_INTERVENTIONS = [
    "pause", "deny", "revoke", "quarantine", "rollback",
    "redirect", "supersede", "compensate", "escalate",
]
EXPECTED_DIGEST = "sha256:030f22b998a6f9c382db5463a4cc55f6d70132d5dd20d880778b5efda9844536"


def require(condition, message):
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main():
    data = json.loads(PATH.read_text())
    require(data.get("schema_version") == "1.0.0", "schema_version")
    require(data.get("record_type") == "stegverse.correctability.publisher_projection", "record_type")
    require(data.get("source_repository") == "StegVerse-Labs/StegCore", "source_repository")
    require(data.get("source_goal") == "CORRECTABILITY-LAYER-001", "source_goal")

    src = data.get("source_validation", {})
    require(src.get("workflow_run_id") == 30774680694, "workflow_run_id")
    require(src.get("job_id") == 91567818006, "job_id")
    require(src.get("fixture_count") == 10, "fixture_count")
    require(src.get("passed_count") == 10, "passed_count")
    require(src.get("artifact_id") == 8841612361, "artifact_id")
    require(src.get("artifact_digest") == EXPECTED_DIGEST, "artifact_digest")

    semantics = data.get("semantics", {})
    for key in (
        "timely_correction_requires_valid_authority",
        "timely_correction_requires_reachable_pathway",
        "timely_correction_requires_enforceable_intervention",
        "late_request_is_not_timely_correction",
        "post_irreversibility_compensation_is_distinct_from_prevention",
    ):
        require(semantics.get(key) is True, key)
    require(semantics.get("allowed_interventions") == EXPECTED_INTERVENTIONS, "allowed_interventions")

    effect = data.get("publisher_effect", {})
    require(effect.get("state") == "VERIFIED_SOURCE_SEMANTICS_PROJECTED", "publisher state")
    for key in (
        "publication_authorized", "release_authorized", "custody_recorded",
        "execution_authorized", "guardian_authority", "admissibility_authority",
    ):
        require(effect.get(key) is False, key)
    require(data.get("manual_user_action_required") is False, "manual_user_action_required")

    print("PASS: bounded correctability projection validated")


if __name__ == "__main__":
    main()
