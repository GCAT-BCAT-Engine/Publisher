#!/usr/bin/env python3
"""
verify_sweep_results.py

Model-level verifier for GCAT/BCAT randomized sweep output.

This verifier checks structure, internal consistency, scalar ranges, and expected
seed-42 sample characteristics for `sweep_randomized_results.json`.

It does not validate any physical/cosmological claim. It only verifies that the
recorded sweep output is coherent under the current in-repo model expectations.

Usage:
    python academic/cosmos/verify_sweep_results.py academic/cosmos/sweep_randomized_results.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

EXPECTED_OUTCOMES = {"ALLOW", "DENY", "FAIL_CLOSED"}
EXPECTED_TEST_NAME = "governance_random_sweep_randomized"
EXPECTED_MODE = "enforced"
DEFAULT_TOLERANCE = 1e-9


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def pass_check(message: str) -> None:
    print(f"PASS: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)
    pass_check(message)


def require_number(value: Any, name: str) -> float:
    require(isinstance(value, (int, float)) and not isinstance(value, bool), f"{name} is numeric")
    require(math.isfinite(float(value)), f"{name} is finite")
    return float(value)


def require_probability(value: Any, name: str) -> float:
    numeric = require_number(value, name)
    require(0.0 <= numeric <= 1.0, f"{name} is within [0, 1]")
    return numeric


def require_simplex(state: Any, name: str, tolerance: float) -> None:
    require(isinstance(state, dict), f"{name} is an object")
    require(set(state.keys()) == {"g", "c", "a", "t"}, f"{name} has g/c/a/t keys")
    values = [require_number(state[key], f"{name}.{key}") for key in ("g", "c", "a", "t")]
    require(all(value >= -tolerance for value in values), f"{name} has non-negative components")
    require(abs(sum(values) - 1.0) <= tolerance, f"{name} sums to 1.0 within tolerance")


def load_json(path: Path) -> dict[str, Any]:
    require(path.exists(), f"input file exists: {path}")
    require(path.is_file(), f"input path is a file: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"input file is valid JSON: {exc}")
    require(isinstance(data, dict), "top-level JSON value is an object")
    return data


def verify_top_level(data: dict[str, Any]) -> int:
    require(data.get("test") == EXPECTED_TEST_NAME, "test name matches expected sweep")
    require(data.get("mode") == EXPECTED_MODE, "mode is enforced")

    samples = require_number(data.get("samples"), "samples")
    require(samples > 0 and samples.is_integer(), "samples is a positive integer")
    return int(samples)


def verify_counts(data: dict[str, Any], samples: int, tolerance: float) -> None:
    counts = data.get("counts")
    frequencies = data.get("frequencies")

    require(isinstance(counts, dict), "counts is an object")
    require(isinstance(frequencies, dict), "frequencies is an object")
    require(set(counts.keys()) == EXPECTED_OUTCOMES, "counts has expected outcome keys")
    require(set(frequencies.keys()) == EXPECTED_OUTCOMES, "frequencies has expected outcome keys")

    total = 0
    for outcome in EXPECTED_OUTCOMES:
        count = require_number(counts[outcome], f"counts.{outcome}")
        require(count >= 0 and count.is_integer(), f"counts.{outcome} is a non-negative integer")
        total += int(count)

        frequency = require_probability(frequencies[outcome], f"frequencies.{outcome}")
        expected_frequency = int(count) / samples
        require(abs(frequency - expected_frequency) <= tolerance, f"frequencies.{outcome} matches counts/samples")

    require(total == samples, "count total equals samples")
    require(abs(sum(float(frequencies[outcome]) for outcome in EXPECTED_OUTCOMES) - 1.0) <= tolerance, "frequencies sum to 1.0")


def verify_scalar(data: dict[str, Any], samples: int, tolerance: float) -> None:
    scalar = data.get("scalar")
    require(isinstance(scalar, dict), "scalar is an object")

    mean = require_probability(scalar.get("mean"), "scalar.mean")
    minimum = require_probability(scalar.get("min"), "scalar.min")
    maximum = require_probability(scalar.get("max"), "scalar.max")
    variance = require_number(scalar.get("variance"), "scalar.variance")
    require(variance >= -tolerance, "scalar.variance is non-negative")
    require(minimum <= mean <= maximum, "scalar min <= mean <= max")

    by_outcome = scalar.get("by_outcome")
    counts = data.get("counts")
    require(isinstance(by_outcome, dict), "scalar.by_outcome is an object")
    require(set(by_outcome.keys()) == EXPECTED_OUTCOMES, "scalar.by_outcome has expected outcome keys")

    scalar_total = 0
    all_scalars: list[float] = []
    for outcome in EXPECTED_OUTCOMES:
        values = by_outcome[outcome]
        require(isinstance(values, list), f"scalar.by_outcome.{outcome} is a list")
        require(len(values) == int(counts[outcome]), f"scalar.by_outcome.{outcome} length matches count")
        for index, value in enumerate(values):
            numeric = require_probability(value, f"scalar.by_outcome.{outcome}[{index}]")
            all_scalars.append(numeric)
        scalar_total += len(values)

    require(scalar_total == samples, "total scalar records equals samples")
    if all_scalars:
        computed_mean = sum(all_scalars) / len(all_scalars)
        computed_min = min(all_scalars)
        computed_max = max(all_scalars)
        computed_variance = sum((value - computed_mean) ** 2 for value in all_scalars) / len(all_scalars)
        require(abs(computed_mean - mean) <= tolerance, "scalar.mean matches by_outcome values")
        require(abs(computed_min - minimum) <= tolerance, "scalar.min matches by_outcome values")
        require(abs(computed_max - maximum) <= tolerance, "scalar.max matches by_outcome values")
        require(abs(computed_variance - variance) <= tolerance, "scalar.variance matches by_outcome values")


def verify_boundary_proximity(data: dict[str, Any], tolerance: float) -> None:
    boundary = data.get("boundary_proximity")
    counts = data.get("counts")
    require(isinstance(boundary, dict), "boundary_proximity is an object")

    mean = require_number(boundary.get("mean"), "boundary_proximity.mean")
    minimum = require_number(boundary.get("min"), "boundary_proximity.min")
    maximum = require_number(boundary.get("max"), "boundary_proximity.max")
    count = require_number(boundary.get("count"), "boundary_proximity.count")

    require(count >= 0 and count.is_integer(), "boundary_proximity.count is a non-negative integer")
    require(int(count) == int(counts["DENY"]), "boundary_proximity.count equals DENY count")
    require(0.0 <= minimum <= mean <= maximum <= 0.25 + tolerance, "boundary proximity values are ordered within model range")


def verify_results(data: dict[str, Any], samples: int, tolerance: float) -> None:
    results = data.get("results")
    require(isinstance(results, list), "results is a list")
    require(len(results) == samples, "results length equals samples")

    counts = {outcome: 0 for outcome in EXPECTED_OUTCOMES}
    boundary_values: list[float] = []

    for expected_index, record in enumerate(results):
        require(isinstance(record, dict), f"results[{expected_index}] is an object")
        require(record.get("sample") == expected_index, f"results[{expected_index}].sample matches index")
        require_simplex(record.get("state_before"), f"results[{expected_index}].state_before", tolerance)
        require_simplex(record.get("projected_state"), f"results[{expected_index}].projected_state", tolerance)

        outcome = record.get("outcome")
        require(outcome in EXPECTED_OUTCOMES, f"results[{expected_index}].outcome is recognized")
        counts[outcome] += 1

        scalar = require_probability(record.get("scalar"), f"results[{expected_index}].scalar")
        reality = record.get("reality")
        require(isinstance(reality, str) and len(reality) > 0, f"results[{expected_index}].reality is non-empty")

        invariant_after = require_number(record.get("invariant_after"), f"results[{expected_index}].invariant_after")
        if outcome == "ALLOW":
            require(invariant_after <= tolerance, f"results[{expected_index}] ALLOW has invariant_after <= 0")
        elif outcome == "DENY":
            require(invariant_after > tolerance, f"results[{expected_index}] DENY has invariant_after > 0")
            boundary_values.append(invariant_after)

        require(0.0 <= scalar <= 1.0, f"results[{expected_index}].scalar remains within model range")

    for outcome in EXPECTED_OUTCOMES:
        require(counts[outcome] == int(data["counts"][outcome]), f"result outcome count matches counts.{outcome}")

    if boundary_values:
        boundary = data["boundary_proximity"]
        require(abs(sum(boundary_values) / len(boundary_values) - float(boundary["mean"])) <= 1e-6, "boundary mean matches result invariants")
        require(abs(min(boundary_values) - float(boundary["min"])) <= 1e-6, "boundary min matches result invariants")
        require(abs(max(boundary_values) - float(boundary["max"])) <= 1e-6, "boundary max matches result invariants")


def verify_seed_42_expectations(data: dict[str, Any]) -> None:
    if data.get("seed") != 42 or data.get("samples") != 100:
        print("SKIP: seed-42 deterministic expectations apply only to seed=42 and samples=100")
        return

    require(data["counts"] == {"ALLOW": 0, "DENY": 100, "FAIL_CLOSED": 0}, "seed=42 sample=100 outcome counts match recorded expectation")
    require(abs(float(data["scalar"]["mean"]) - 0.38594275823540847) <= DEFAULT_TOLERANCE, "seed=42 scalar mean matches recorded expectation")
    require(abs(float(data["boundary_proximity"]["mean"]) - 0.216707) <= 1e-6, "seed=42 boundary mean matches rounded recorded expectation")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify GCAT/BCAT sweep result JSON at model level.")
    parser.add_argument("path", nargs="?", default="academic/cosmos/sweep_randomized_results.json", help="Path to sweep_randomized_results.json")
    parser.add_argument("--tolerance", type=float, default=DEFAULT_TOLERANCE, help="Floating-point tolerance")
    args = parser.parse_args()

    data = load_json(Path(args.path))
    samples = verify_top_level(data)
    verify_counts(data, samples, args.tolerance)
    verify_scalar(data, samples, args.tolerance)
    verify_boundary_proximity(data, args.tolerance)
    verify_results(data, samples, args.tolerance)
    verify_seed_42_expectations(data)

    print("PASS: sweep result verification complete")
    print("NOTE: This verifier confirms model-level consistency only; it does not validate physical/cosmological claims.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
