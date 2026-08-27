#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "governance-observatory-publication-awareness.json"

def require(condition, message):
    if not condition:
        raise SystemExit(f"FAIL: {message}")

def main():
    data = json.loads(PATH.read_text())
    require(data.get("schema_version") == "1.0.0", "schema_version")
    require(data.get("record_type") == "stegverse.governance_observatory.publisher_publication_awareness", "record_type")
    require(data.get("source_repository") == "StegVerse-Labs/governance-observatory", "source_repository")
    src = data.get("source_publication", {})
    require(src.get("state") == "PUBLISHED", "source publication state")
    require(src.get("merge_commit") == "52d9a8f596ade145f5b08e44e98395d328476ecc", "source merge")
    for key in ("publication_gate_run","self_management_readiness_run","validate_governance_observatory_run","val_gov_obs_run","post_merge_verify_run"):
        require(isinstance(src.get(key), int), key)
    release = data.get("source_release", {})
    require(release.get("state") == "RELEASED", "release state")
    require(release.get("version") == "0.1.0", "release version")
    require(release.get("tag_name") == "v0.1.0", "release tag")
    require(release.get("release_id") == 377486341, "release id")
    require(release.get("release_url") == "https://github.com/StegVerse-Labs/governance-observatory/releases/tag/v0.1.0", "release url")
    require(release.get("release_state_head") == "31afc11745507e4764c2c9f44be1e5143e920ef1", "release head")
    require(release.get("release_workflow_run") == 33025454602, "release workflow run")
    target = data.get("target_reconciliation", {})
    require(target.get("site") == "CONFIRMED_EXISTING_TARGET_NATIVE_INTEGRATION", "site reconciliation")
    require(target.get("admissibility_wiki") == "CONFIRMED_EXISTING_TARGET_NATIVE_INTEGRATION", "wiki reconciliation")
    require(target.get("standing_proof_engine") == "CONFIRMED_MERGED_TARGET_INTAKE", "SPE reconciliation")
    effect = data.get("publisher_effect", {})
    require(effect.get("state") == "VERIFIED_RELEASE_AWARENESS_PROJECTED", "publisher state")
    for key in ("publication_authorized","release_authorized","custody_recorded","execution_authorized","guardian_authority","admissibility_authority"):
        require(effect.get(key) is False, key)
    aegis = data.get("aegisai_boundary", {})
    require(aegis.get("source_only") is True, "AEGISAI source-only")
    require(aegis.get("runtime_validated") is False, "AEGISAI runtime boundary")
    require(aegis.get("framework_promoted") is False, "AEGISAI framework boundary")
    require(data.get("manual_user_action_required") is False, "manual user action")
    print("PASS: Governance Observatory v0.1.0 release awareness projection validated")

if __name__ == "__main__":
    main()
