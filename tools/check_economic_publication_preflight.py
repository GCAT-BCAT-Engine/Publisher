"""Check source-only economic publication preflight; never perform publication."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "data/economy/economic-publication-preflight.v1.json"
VOL3 = ROOT / "papers/entity-economy-volume-iii-sovereign-ai-economics.md"
APPROVED = ROOT / "papers/StegVerse_Private_State_Economy_White_Paper_v0.1.md"

def check(value: dict) -> None:
    assert value["schema"] == "stegverse.publisher.economic-publication-preflight/v1"
    assert value["goal_task_id"] == "ECOSYSTEM-ECONOMIC-WHITEPAPER-GATED-ROADMAP-001"
    assert value["current_observational_cosv"] == "10100000103000"
    assert value["authority_effect"] == "NONE"
    assert value["evidence_class"] == "SOURCE_ONLY_PRE_ADMISSION_DIAGNOSTIC"
    assert value["status"] == "SOURCE_PREFLIGHT_FAIL_CLOSED"
    assert value["runtime_manifest_invoked"] is False
    assert value["runtime_disposition"] is None
    assert value["owner_document_approval"]["recorded"] is True
    assert value["owner_document_approval"]["manuscript_replacement_required"] is False
    original, third = value["candidates"]
    assert original["owner_approved"] is True
    assert original["source_on_publisher_main"] is False
    assert original["governed_published"] is False
    assert original["source_commit"] == "f9a140d02e162c8284db7fe22b9093e70c25207a"
    assert original["sha256"] == "3329a0c47161eb4613c32bbc5e0a393116f395cb8fa78368ed21fed8775c3dca"
    assert not APPROVED.exists(), "Original PR #72 paper unexpectedly present on main: update preflight after authenticated reconciliation"
    assert third["owner_approved"] is True and third["governed_published"] is False
    assert third["sha256"] == hashlib.sha256(VOL3.read_bytes()).hexdigest()
    reviews = value["reviewer_evidence"]
    assert reviews["verified_review_decisions"] is False
    assert reviews["economics_review_receipt"] is None and reviews["legal_review_receipt"] is None
    assert [p["predicate"] for p in value["preflight_predicates"]] == [
        "REVIEW_EVIDENCE_RECONCILED_TO_APPROVED_EXACT_SOURCE",
        "PUBLISHER_PAPERS_NATIVE_RUNTIME_CONSUMER",
        "ORIGINAL_AUTHENTIC_RUNTIME_INTR_AND_MASTER_RECORDS_CLOSURE",
    ]
    assert [p["status"] for p in value["preflight_predicates"]] == [
        "FAIL_CLOSED", "FAIL_CLOSED", "NOT_ATTEMPTED"
    ]
    assert all(p["evidence_refs"] and p["correction"] for p in value["preflight_predicates"])
    assert value["requested_target"]["repository"] == "GCAT-BCAT-Engine/Publisher"
    assert value["requested_target"]["path_prefix"] == "papers/"
    assert value["requested_target"]["publication_execution_requested"] is False
    a = value["authorization"]
    assert a["manifest_prepared"] is False and a["mutation_authorized"] is False
    assert all(a[k] is None for k in (
        "external_intr_allow","master_records_receipt","publisher_release_receipt","site_deployed_readback"
    ))
    assert value["site_benchmarks"] == {"count":16,"all_status":"NOT_VERIFIED","no_promotion_authorized":True}

if __name__ == "__main__":
    check(json.loads(DOC.read_text(encoding="utf-8")))
    print("PASS: approved source exact identity, Volume III digest and non-ALLOW preflight boundaries")
