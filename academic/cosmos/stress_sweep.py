#!/usr/bin/env python3
"""
stress_sweep.py

Multi-seed internal stress suite for the GCAT/BCAT randomized cosmos sweep.

This script runs deterministic seeds through the in-repo model and checks
model-level invariants only. It does not validate physical or cosmological
claims.

Usage:
    python academic/cosmos/stress_sweep.py
    python academic/cosmos/stress_sweep.py --samples 100 --seeds 1,7,13,42,101
"""

from __future__ import annotations

import argparse
import json
import math
import tempfile
from pathlib import Path
from typing import Any

from governance_random_sweep import run_randomized_sweep

DEFAULT_SEEDS = [1, 7, 13, 42, 101]
DEFAULT_SAMPLES = 100
EXPECTED_OUTCOMES = {"ALLOW", "DENY", "FAIL_CLOSED"}

# These thresholds are model-health thresholds, not physics/cosmology thresholds.
MAX_FAIL_CLOSED_RATE = 0.0
MAX_ALLOW_RATE = 0.05
MIN_DENY_RATE = 0.95
MIN_SCALAR_VALUE = 0.0
MAX_SCALAR_VALUE = 1.0
MAX_BOUNDARY_PROXIMITY = 0.25


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def pass_check(message: str) -> None:
    print(f"PASS: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)
    pass_check(message)


def parse_seeds(value: str) -> list[int]:
    try:
        seeds = [int(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"seeds must be comma-separated integers: {exc}") from exc

    if not seeds:
        raise argparse.ArgumentTypeError("at least one seed is required")

    return seeds


def require_number(value: Any, name: str) -> float:
    require(isinstance(value, (int, float)) and not isinstance(value, bool), f"{name} is numeric")
    numeric = float(value)
    require(math.isfinite(numeric), f"{name} is finite")
    return numeric


def collect_scalars(result: dict[str, Any]) -> list[float]:
    by_outcome = result["scalar"]["by_outcome"]
    scalars: list[float] = []
    for outcome in EXPECTED_OUTCOMES:
        values = by_outcome[outcome]
        require(isinstance(values, list), f"scalar.by_outcome.{outcome} is a list")
        scalars.extend(float(value) for value in values)
    return scalars


def verify_single_run(seed: int, samples: int, result: dict[str, Any]) -> dict[str, Any]:
    print(f"\n=== Verifying seed={seed}, samples={samples} ===")

    require(result.get("test") == "governance_random_sweep_randomized", "test name matches expected sweep")
    require(result.get("mode") == "enforced", "mode is enforced")
    require(result.get("seed") == seed, "result seed matches requested seed")
    require(result.get("samples") == samples, "result samples match requested samples")

    counts = result.get("counts")
    frequencies = result.get("frequencies")
    require(isinstance(counts, dict), "counts is an object")
    require(isinstance(frequencies, dict), "frequencies is an object")
    require(set(counts.keys()) == EXPECTED_OUTCOMES, "counts has expected outcome keys")
    require(set(frequencies.keys()) == EXPECTED_OUTCOMES, "frequencies has expected outcome keys")

    total_count = sum(int(counts[outcome]) for outcome in EXPECTED_OUTCOMES)
    require(total_count == samples, "counts sum to samples")

    fail_closed_rate = float(frequencies["FAIL_CLOSED"])
    allow_rate = float(frequencies["ALLOW"])
    deny_rate = float(frequencies["DENY"])

    require(fail_closed_rate <= MAX_FAIL_CLOSED_RATE, "FAIL_CLOSED rate remains at zero for valid generated states")
    require(allow_rate <= MAX_ALLOW_RATE, "ALLOW rate remains within sparse-boundary expectation")
    require(deny_rate >= MIN_DENY_RATE, "DENY rate remains within dense-interior expectation")

    scalars = collect_scalars(result)
    require(len(scalars) == samples, "scalar count equals samples")
    require(all(MIN_SCALAR_VALUE <= scalar <= MAX_SCALAR_VALUE for scalar in scalars), "all scalars remain within [0, 1]")

    boundary = result.get("boundary_proximity")
    require(isinstance(boundary, dict), "boundary_proximity is an object")
    boundary_count = int(require_number(boundary.get("count"), "boundary_proximity.count"))
    require(boundary_count == int(counts["DENY"]), "boundary count equals DENY count")

    if boundary_count > 0:
        boundary_mean = require_number(boundary.get("mean"), "boundary_proximity.mean")
        boundary_min = require_number(boundary.get("min"), "boundary_proximity.min")
        boundary_max = require_number(boundary.get("max"), "boundary_proximity.max")
        require(0.0 <= boundary_min <= boundary_mean <= boundary_max <= MAX_BOUNDARY_PROXIMITY, "boundary proximity stays in model range")

    return {
        "seed": seed,
        "samples": samples,
        "counts": counts,
        "frequencies": frequencies,
        "scalar": {
            "mean": result["scalar"]["mean"],
            "min": result["scalar"]["min"],
            "max": result["scalar"]["max"],
            "variance": result["scalar"]["variance"],
        },
        "boundary_proximity": boundary,
    }


def run_stress_suite(seeds: list[int], samples: int, output_path: Path) -> dict[str, Any]:
    summaries = []

    with tempfile.TemporaryDirectory() as temporary_directory:
        temp_path = Path(temporary_directory)
        for seed in seeds:
            stats_path = temp_path / f"stress_stats_seed_{seed}.json"
            result = run_randomized_sweep(samples_per_phase=samples, seed=seed, stats_path=str(stats_path))
            summaries.append(verify_single_run(seed, samples, result))

    report = {
        "test": "gcat_bcat_cosmos_stress_sweep",
        "mode": "model_level_only",
        "samples_per_seed": samples,
        "seeds": seeds,
        "thresholds": {
            "max_fail_closed_rate": MAX_FAIL_CLOSED_RATE,
            "max_allow_rate": MAX_ALLOW_RATE,
            "min_deny_rate": MIN_DENY_RATE,
            "scalar_range": [MIN_SCALAR_VALUE, MAX_SCALAR_VALUE],
            "max_boundary_proximity": MAX_BOUNDARY_PROXIMITY,
        },
        "runs": summaries,
        "note": "This report verifies model-level sweep behavior only; it does not validate physical or cosmological claims.",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run multi-seed model-level GCAT/BCAT cosmos sweep stress tests.")
    parser.add_argument("--samples", type=int, default=DEFAULT_SAMPLES, help="Samples per seed")
    parser.add_argument("--seeds", type=parse_seeds, default=DEFAULT_SEEDS, help="Comma-separated deterministic seeds")
    parser.add_argument("--output", type=Path, default=Path("stress_sweep_results.json"), help="Output JSON report path")
    args = parser.parse_args()

    require(args.samples > 0, "samples is positive")
    report = run_stress_suite(args.seeds, args.samples, args.output)

    print("\nPASS: multi-seed stress sweep complete")
    print(f"Report saved to: {args.output}")
    print(report["note"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
