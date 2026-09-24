#!/usr/bin/env python3
"""Verify exact draft white-paper candidate identity, not publication authority."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
candidate = json.loads((ROOT/"data/economy/private-state-economy-editorial-candidate.v0.1.json").read_text())
assert candidate["schema"] == "stegverse.publisher.editorial-source-candidate/v1"
assert candidate["authority_effect"] == "NONE"
assert candidate["status"] == "DRAFT_SOURCE_BOUND_INDEPENDENT_REVIEW_PENDING"
assert candidate["goal_task_id"] == "ECOSYSTEM-ECONOMIC-WHITEPAPER-GATED-ROADMAP-001"
source = candidate["source"]
assert source["path"] == "papers/StegVerse_Private_State_Economy_White_Paper_v0.1.md"
computed = hashlib.sha256((ROOT/source["path"]).read_bytes()).hexdigest()
assert computed == source["sha256"], ("reviewed source hash changed; invalidate stale candidate",computed,source["sha256"])
assert candidate["editorial_review"]["all_original_pdf_page_images_examined"] is True
assert candidate["editorial_review"]["independent_economics_review_approved"] is False
assert candidate["editorial_review"]["jurisdiction_specific_legal_review_approved"] is False
assert candidate["publication_mutation_authorized"] is False
assert candidate["benchmark_checks_authorized"] is False
assert candidate["runtime_execution_claimed"] is False
assert len(candidate["verified_historical_sources"]) == 2
assert candidate["verified_historical_sources"][0]["source_defect"] == "VISUALLY_BLANK_PAGE_9_AND_RIGHT_MARGIN_CLIPPING_PRIOR_PAGES"
assert all(value is None for value in candidate["missing_evidence"].values())
print("PRIVATE_STATE_ECONOMY_EXACT_SOURCE_CANDIDATE_PASS",computed)
