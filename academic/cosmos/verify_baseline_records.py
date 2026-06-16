#!/usr/bin/env python3
"""
verify_baseline_records.py

Verifier for GCAT/BCAT cosmos baseline registry and future baseline result records.

This verifier checks that baseline files preserve claim-layer discipline and do
not silently upgrade analogy/hypothesis records into validated physical theory.

Usage:
    python academic/cosmos/verify_baseline_records.py
    python academic/cosmos/verify_baseline_records.py --registry academic/cosmos/baselines/claim_registry.json
    python academic/cosmos/verify_baseline_records.py --results-dir academic/cosmos/baselines/results
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ALLOWED_CLAIM_LAYERS = {"physics_analogy", "physics_hypothesis"}
ALLOWED_VALIDATION_STATUS = {
    "cataloged",
    "model_level_reproducible",
    "internal_stress_tested",
    "external_baseline_planned",
    "external_baseline_scaffolded",
    "external_baseline_compared",
    "validated_physical_result_candidate",
}
ALLOWED_RESULT_VALUES = {
    "fit",
    "weak_correlation",
    "no_result",
    "contradiction",
    "not_testable_yet",
}
DISALLOWED_CLAIMS = {
    "validated physical theory",
    "replacement for quantum mechanics",
    "replacement for general relativity",
    "proof of dark matter",
    "proof of dark energy",
    "completed cosmological validation",
}
REQUIRED_REGISTRY_CLAIM_FIELDS = {
    "claim_id",
    "title",
    "claim_layer",
    "validation_status",
    "source_artifacts",
    "summary",
    "external_baseline_needed",
    "candidate_external_baselines",
    "observable_required",
    "units_or_normalization_required",
    "failure_condition",
    "safe_public_language",
}
REQUIRED_RESULT_FIELDS = {
    "claim_id",
    "claim_layer",
    "artifact",
    "external_baseline",
    "observable",
    "units",
    "normalization",
    "input_data",
    "method",
    "metric",
    "result",
    "limitations",
    "does_not_claim",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def pass_check(message: str) -> None:
    print(f"PASS: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)
    pass_check(message)


def load_json(path: Path) -> Any:
    require(path.exists(), f"file exists: {path}")
    require(path.is_file(), f"path is file: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"valid JSON: {path}: {exc}")


def require_non_empty_string(value: Any, name: str) -> None:
    require(isinstance(value, str) and bool(value.strip()), f"{name} is a non-empty string")


def require_string_list(value: Any, name: str) -> None:
    require(isinstance(value, list), f"{name} is a list")
    require(all(isinstance(item, str) and item.strip() for item in value), f"{name} contains only non-empty strings")


def verify_registry(registry_path: Path) -> set[str]:
    data = load_json(registry_path)
    require(isinstance(data, dict), "registry top-level value is an object")
    require(data.get("registry") == "gcat_bcat_cosmos_claim_registry", "registry name is recognized")
    require_non_empty_string(data.get("version"), "registry.version")
    require_non_empty_string(data.get("status"), "registry.status")
    require_non_empty_string(data.get("scope"), "registry.scope")

    does_not_claim = data.get("does_not_claim")
    require_string_list(does_not_claim, "registry.does_not_claim")
    require(DISALLOWED_CLAIMS.issubset(set(does_not_claim)), "registry preserves required does_not_claim boundaries")

    claim_layers = data.get("claim_layers")
    require_string_list(claim_layers, "registry.claim_layers")
    require(set(claim_layers).issubset(ALLOWED_CLAIM_LAYERS), "registry claim layers stay analogy/hypothesis only")

    validation_values = data.get("validation_status_values")
    require_string_list(validation_values, "registry.validation_status_values")
    require(set(validation_values).issubset(ALLOWED_VALIDATION_STATUS), "registry validation statuses are recognized")

    claims = data.get("claims")
    require(isinstance(claims, list) and claims, "registry.claims is a non-empty list")

    seen_claim_ids: set[str] = set()
    for index, claim in enumerate(claims):
        prefix = f"registry.claims[{index}]"
        require(isinstance(claim, dict), f"{prefix} is an object")
        require(REQUIRED_REGISTRY_CLAIM_FIELDS.issubset(set(claim.keys())), f"{prefix} has required fields")

        claim_id = claim["claim_id"]
        require_non_empty_string(claim_id, f"{prefix}.claim_id")
        require(claim_id not in seen_claim_ids, f"{prefix}.claim_id is unique")
        seen_claim_ids.add(claim_id)

        require_non_empty_string(claim["title"], f"{prefix}.title")
        require(claim["claim_layer"] in ALLOWED_CLAIM_LAYERS, f"{prefix}.claim_layer is allowed")
        require(claim["validation_status"] in ALLOWED_VALIDATION_STATUS, f"{prefix}.validation_status is allowed")
        require_string_list(claim["source_artifacts"], f"{prefix}.source_artifacts")
        require_non_empty_string(claim["summary"], f"{prefix}.summary")
        require(claim["external_baseline_needed"] is True, f"{prefix}.external_baseline_needed is true")
        require_string_list(claim["candidate_external_baselines"], f"{prefix}.candidate_external_baselines")
        require_non_empty_string(claim["observable_required"], f"{prefix}.observable_required")
        require_non_empty_string(claim["units_or_normalization_required"], f"{prefix}.units_or_normalization_required")
        require_non_empty_string(claim["failure_condition"], f"{prefix}.failure_condition")
        require_non_empty_string(claim["safe_public_language"], f"{prefix}.safe_public_language")

    return seen_claim_ids


def verify_result_record(path: Path, known_claim_ids: set[str]) -> None:
    data = load_json(path)
    require(isinstance(data, dict), f"{path} top-level value is an object")
    require(REQUIRED_RESULT_FIELDS.issubset(set(data.keys())), f"{path} has required result fields")

    claim_id = data["claim_id"]
    require_non_empty_string(claim_id, f"{path}.claim_id")
    require(claim_id in known_claim_ids, f"{path}.claim_id exists in claim registry")
    require(data["claim_layer"] in ALLOWED_CLAIM_LAYERS, f"{path}.claim_layer is allowed")
    require_non_empty_string(data["artifact"], f"{path}.artifact")
    require_non_empty_string(data["external_baseline"], f"{path}.external_baseline")
    require_non_empty_string(data["observable"], f"{path}.observable")
    require_non_empty_string(data["units"], f"{path}.units")
    require_non_empty_string(data["normalization"], f"{path}.normalization")
    require_non_empty_string(data["input_data"], f"{path}.input_data")
    require_non_empty_string(data["method"], f"{path}.method")
    require_non_empty_string(data["metric"], f"{path}.metric")
    require(data["result"] in ALLOWED_RESULT_VALUES, f"{path}.result is recognized")
    require_string_list(data["limitations"], f"{path}.limitations")
    require_string_list(data["does_not_claim"], f"{path}.does_not_claim")
    require("validated physical theory" in set(data["does_not_claim"]), f"{path}.does_not_claim preserves validated-physics boundary")

    if data["result"] == "fit":
        require("limitations" in data and data["limitations"], f"{path}.fit result still includes limitations")
        require("validated physical theory" in data["does_not_claim"], f"{path}.fit result does not silently claim validated physics")


def verify_results_dir(results_dir: Path, known_claim_ids: set[str]) -> None:
    if not results_dir.exists():
        print(f"SKIP: no results directory present: {results_dir}")
        return

    require(results_dir.is_dir(), f"results path is a directory: {results_dir}")
    result_files = sorted(results_dir.glob("*.json"))
    if not result_files:
        print(f"SKIP: no baseline result records present in {results_dir}")
        return

    for path in result_files:
        verify_result_record(path, known_claim_ids)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify GCAT/BCAT cosmos baseline registry and result records.")
    parser.add_argument("--registry", type=Path, default=Path("academic/cosmos/baselines/claim_registry.json"), help="Path to claim_registry.json")
    parser.add_argument("--results-dir", type=Path, default=Path("academic/cosmos/baselines/results"), help="Path to baseline result record directory")
    args = parser.parse_args()

    known_claim_ids = verify_registry(args.registry)
    verify_results_dir(args.results_dir, known_claim_ids)

    print("PASS: baseline registry/result verification complete")
    print("NOTE: This verifier checks record discipline only; it does not validate physical or cosmological claims.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
