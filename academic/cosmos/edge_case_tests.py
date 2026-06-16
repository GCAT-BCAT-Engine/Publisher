#!/usr/bin/env python3
"""
edge_case_tests.py

Edge-case tests for the GCAT/BCAT cosmos sweep core.

These tests cover invalid states, boundary-condition states, projection behavior,
classification behavior, scalar range behavior, and reality labels.

They verify in-repo model behavior only. They do not validate physical or
cosmological claims.

Usage:
    python academic/cosmos/edge_case_tests.py
"""

from __future__ import annotations

import math
import sys
from typing import Any

from governance_random_sweep import (
    bcat_simplex_valid,
    classify_transition,
    compute_invariant,
    compute_scalar,
    generate_random_valid_simplex,
    project_state,
    reality_label,
)

TOLERANCE = 1e-9


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def pass_check(message: str) -> None:
    print(f"PASS: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)
    pass_check(message)


def nearly_equal(left: float, right: float, tolerance: float = TOLERANCE) -> bool:
    return abs(left - right) <= tolerance


def require_simplex(state: dict[str, float], name: str) -> None:
    require(set(state.keys()) == {"g", "c", "a", "t"}, f"{name} has g/c/a/t keys")
    require(all(value >= -TOLERANCE for value in state.values()), f"{name} has non-negative components")
    require(nearly_equal(sum(state.values()), 1.0), f"{name} sums to 1.0")


def test_simplex_validation() -> None:
    valid = {"g": 0.25, "c": 0.25, "a": 0.25, "t": 0.25}
    invalid_sum = {"g": 0.25, "c": 0.25, "a": 0.25, "t": 0.20}
    invalid_negative = {"g": 0.50, "c": 0.50, "a": 0.10, "t": -0.10}

    require(bcat_simplex_valid(valid), "valid simplex is accepted")
    require(not bcat_simplex_valid(invalid_sum), "invalid sum simplex is rejected")
    require(not bcat_simplex_valid(invalid_negative), "negative component simplex is rejected")


def test_invariant_boundaries() -> None:
    ga_axis = {"g": 0.50, "c": 0.0, "a": 0.50, "t": 0.0}
    ct_axis = {"g": 0.0, "c": 0.50, "a": 0.0, "t": 0.50}
    balanced = {"g": 0.25, "c": 0.25, "a": 0.25, "t": 0.25}

    require(nearly_equal(compute_invariant(ga_axis), 0.0), "g/a axis has zero invariant")
    require(nearly_equal(compute_invariant(ct_axis), 0.0), "c/t axis has zero invariant")
    require(nearly_equal(compute_invariant(balanced), 0.25), "balanced simplex has max expected invariant 0.25")


def test_classification_behavior() -> None:
    valid_before = {"g": 0.25, "c": 0.25, "a": 0.25, "t": 0.25}
    allow_projected = {"g": 0.50, "c": 0.0, "a": 0.50, "t": 0.0}
    deny_projected = {"g": 0.25, "c": 0.25, "a": 0.25, "t": 0.25}
    invalid_before = {"g": 0.25, "c": 0.25, "a": 0.25, "t": 0.20}
    invalid_projected = {"g": 0.25, "c": 0.25, "a": 0.25, "t": 0.20}

    outcome, reason = classify_transition(valid_before, allow_projected)
    require(outcome == "ALLOW", "zero-invariant projected state is ALLOW")
    require("<= 0" in reason, "ALLOW reason includes <= 0")

    outcome, reason = classify_transition(valid_before, deny_projected)
    require(outcome == "DENY", "positive-invariant projected state is DENY")
    require("> 0" in reason, "DENY reason includes > 0")

    outcome, reason = classify_transition(invalid_before, allow_projected)
    require(outcome == "FAIL_CLOSED", "invalid initial state fails closed")
    require(reason == "Invalid initial state", "invalid initial state reason is stable")

    outcome, reason = classify_transition(valid_before, invalid_projected)
    require(outcome == "FAIL_CLOSED", "invalid projected state fails closed")
    require(reason == "Projected state invalid", "invalid projected state reason is stable")


def test_projection_behavior() -> None:
    state = {"g": 0.10, "c": 0.20, "a": 0.30, "t": 0.40}
    delta = {"g": -0.50, "c": 0.10, "a": 0.20, "t": 0.20}
    projected = project_state(state, delta)

    require_simplex(projected, "projected state")
    require(projected["g"] == 0.0, "projection clamps negative g to zero")


def test_scalar_behavior() -> None:
    quantum = {"g": 0.50, "c": 0.0, "a": 0.50, "t": 0.0}
    astrophysical = {"g": 0.0, "c": 0.50, "a": 0.0, "t": 0.50}
    balanced = {"g": 0.25, "c": 0.25, "a": 0.25, "t": 0.25}

    require(nearly_equal(compute_scalar(quantum), 0.0), "g/a zero-invariant axis maps to scalar 0.0")
    require(nearly_equal(compute_scalar(astrophysical), 1.0), "c/t zero-invariant axis maps to scalar 1.0")

    balanced_scalar = compute_scalar(balanced)
    require(0.0 <= balanced_scalar <= 1.0, "balanced scalar remains in [0, 1]")

    for scalar in [0.0, 0.1, 0.3, 0.45, 0.55, 0.7, 0.9, 1.0]:
        label = reality_label(scalar)
        require(isinstance(label, str) and bool(label), f"reality label is stable for scalar {scalar}")


def test_random_generator_smoke() -> None:
    for index in range(10):
        state = generate_random_valid_simplex()
        require_simplex(state, f"random simplex {index}")


def main() -> int:
    tests = [
        test_simplex_validation,
        test_invariant_boundaries,
        test_classification_behavior,
        test_projection_behavior,
        test_scalar_behavior,
        test_random_generator_smoke,
    ]

    for test in tests:
        print(f"\n=== {test.__name__} ===")
        test()

    print("\nPASS: edge-case tests complete")
    print("NOTE: These tests verify model-level behavior only; they do not validate physical or cosmological claims.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
