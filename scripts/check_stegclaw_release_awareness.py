#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "stegclaw-release-awareness.json"

def require(condition, message):
    if not condition:
        raise SystemExit(f"FAIL: {message}")

def main():
    data = json.loads(PATH.read_text(encoding="utf-8"))
    require(data.get("schema_version") == "1.0.0", "schema_version")
    require(data.get("record_type") == "stegverse.stegclaw.publisher_release_awareness", "record_type")
    require(data.get("source_repository") == "Data-Continuation/StegClaw", "source_repository")
    src = data.get("source_release", {})
    require(src.get("state") == "RELEASED", "release state")
    require(src.get("version") == "1.0.0", "release version")
    require(src.get("tag_name") == "v1.0.0", "release tag")
    require(src.get("release_id") == 381434394, "release id")
    require(src.get("release_target") == "6b89a4bfb3d4c2fcc61e6cccaa4f292fb4d58cdb", "release target")
    require(src.get("validation_run") == 33650991623, "validation run")
    require(src.get("validation_artifact_id") == 9854745757, "validation artifact")
    require(src.get("validation_artifact_digest") == "sha256:90d18ccac5f28ca893c5347ebeaeb8828503b166b5ce6a45be794110ebd55fc5", "artifact digest")
    upstream = data.get("upstream_state", {})
    require(upstream.get("ecosystem_handoff") == "STEGCLAW_ECOSYSTEM_HANDOFF_VERIFIED", "ecosystem handoff")
    require(upstream.get("release_gate") == "ALLOW", "release gate")
    effect = data.get("publisher_effect", {})
    require(effect.get("state") == "VERIFIED_RELEASE_AWARENESS_PROJECTED", "publisher state")
    for key in ("publication_authorized","release_authorized","custody_recorded","execution_authorized","runtime_activation_claimed","guardian_authority","admissibility_authority"):
        require(effect.get(key) is False, key)
    require(data.get("authority_effect") == "NONE", "authority effect")
    require(data.get("manual_user_action_required") is False, "manual action")
    print("PASS: StegClaw v1.0.0 Publisher release awareness validated")

if __name__ == "__main__":
    main()
