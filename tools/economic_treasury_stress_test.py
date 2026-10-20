#!/usr/bin/env python3
"""Deterministic liquidity and treasury stress test for roadmap benchmark S5_STRESS.

S5_STRESS (StegVerse-Labs/Site:data/economy/public-release-benchmarks.v1.json) requires
"realistic downturn, selling pressure, redemption, rewards and service continuity tested
with attributable inputs". This evaluator implements that test over a declared scenario
file (schema ``stegverse.publisher.treasury-stress-scenarios/v1``):

* every numeric input carries ``value``, a public-safe ``source_ref`` and an
  ``attribution``; an input without them is refused, never defaulted;
* every scenario declares all five stress dimensions (``downturn``, ``selling_pressure``,
  ``redemption``, ``rewards``, ``service_continuity``);
* each period, the volatile share of the treasury falls by the downturn plus the price
  impact of selling pressure, then redemptions, rewards and operating cost are paid and
  revenue is received. Arithmetic is exact (``fractions.Fraction``); output is rendered
  deterministically.

A scenario is ALLOW only when all three predicates hold in every period:
``solvency`` (treasury never negative), ``coverage`` (treasury / outstanding redeemable
claims never below the declared floor) and ``service_continuity`` (runway in periods of
operating cost never below the declared floor). Each failure names its predicate and
the first failing period. A run with any failing scenario is DENY and carries the six
fields, naming the first failing predicate, its scenario and period; ALLOW carries none.
Values are rendered exactly: a terminating decimal, otherwise numerator/denominator.

The result is research evidence (``evidence_class: SOURCE_IMPLEMENTED`` here,
``CI_VALIDATED`` once this module's workflow passes; ``FIXTURE_NOT_EVIDENCE`` for a
fixture file). It never marks S5_STRESS
complete: realism requires owner-accepted input sources, and completion stays a
Publisher-governed closure through Master Records. Inputs declared synthetic are refused
unless the scenario file declares itself a fixture. Stdlib only; no network,
credential or write outside ``--output``.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

SCHEMA = "stegverse.publisher.treasury-stress-scenarios/v1"
RESULT_SCHEMA = "stegverse.publisher.treasury-stress-result/v1"
BENCHMARK_ID = "S5_STRESS"
GOAL = "ECOSYSTEM-ECONOMIC-WHITEPAPER-GATED-ROADMAP-001"
RETRY = "python3 tools/economic_treasury_stress_test.py <scenarios.json>"
DIMENSIONS = ("downturn", "selling_pressure", "redemption", "rewards", "service_continuity")
TREASURY_INPUTS = ("treasury_value", "volatile_share", "redeemable_claims", "revenue_per_period")
DIMENSION_INPUTS = {
    "downturn": ("price_drop_per_period",),
    "selling_pressure": ("sold_share_per_period", "price_impact_per_unit_sold"),
    "redemption": ("redemption_rate_per_period",),
    "rewards": ("rewards_per_period",),
    "service_continuity": ("operating_cost_per_period", "minimum_runway_periods"),
}
FRACTION_INPUTS = {"volatile_share", "price_drop_per_period", "sold_share_per_period",
                   "price_impact_per_unit_sold", "redemption_rate_per_period"}
_REF = re.compile(r"^(https://|org-ledger://|master-records://|publisher://|site://)[^\s]{1,500}$")
_ID = re.compile(r"^[A-Za-z0-9_.-]{1,80}$")
MAX_PERIODS = 120


class Refused(Exception):
    def __init__(self, code: str, predicate: str, repair: str, **evidence: Any) -> None:
        super().__init__(code)
        self.result = {"disposition": "FAIL_CLOSED", "failure_code": code, "failed_predicate": predicate,
                       "required_evidence_or_repair": repair, "retry_entrypoint": RETRY,
                       "owning_existing_goal": GOAL, "next_attempt": "after the scenario file is corrected",
                       "evidence": evidence}


def _input(block: Any, name: str, where: str, allow_synthetic: bool) -> Fraction:
    item = block.get(name) if isinstance(block, dict) else None
    if not isinstance(item, dict):
        raise Refused("STRESS_INPUT_MISSING", f"{where}.{name} is declared", "declare the input with value, source_ref and attribution",
                      input=f"{where}.{name}")
    if not (isinstance(item.get("source_ref"), str) and _REF.match(item["source_ref"])
            and isinstance(item.get("attribution"), str) and item["attribution"].strip()):
        raise Refused("STRESS_INPUT_NOT_ATTRIBUTABLE", f"{where}.{name} carries a public-safe source_ref and an attribution",
                      "attribute the input to its public source", input=f"{where}.{name}")
    if item.get("synthetic") is not False and not allow_synthetic:
        raise Refused("STRESS_INPUT_SYNTHETIC", f"{where}.{name} is declared non-synthetic",
                      "replace the input with an attributable observed value, or mark the file a fixture",
                      input=f"{where}.{name}")
    raw = item.get("value")
    if isinstance(raw, bool) or not isinstance(raw, (int, str)):
        raise Refused("STRESS_INPUT_OUT_OF_RANGE", f"{where}.{name} is an integer or a decimal string",
                      "write the value as an integer or a decimal string (exact arithmetic)", input=f"{where}.{name}")
    try:
        value = Fraction(raw)
    except (ValueError, ZeroDivisionError):
        raise Refused("STRESS_INPUT_OUT_OF_RANGE", f"{where}.{name} parses exactly", "fix the number", input=f"{where}.{name}") from None
    if value < 0 or (name in FRACTION_INPUTS and value > 1):
        raise Refused("STRESS_INPUT_OUT_OF_RANGE", f"{where}.{name} is within its range",
                      "fractions are in [0, 1]; amounts are non-negative", input=f"{where}.{name}", value=str(raw))
    return value


def _number(value: Fraction) -> str:
    """Exact text: a terminating decimal when one exists, otherwise numerator/denominator."""
    if value.denominator == 1:
        return str(value.numerator)
    rest = value.denominator
    for prime in (2, 5):
        while rest % prime == 0:
            rest //= prime
    if rest != 1:
        return f"{value.numerator}/{value.denominator}"
    places = 0
    while (value * 10 ** places).denominator != 1:
        places += 1
    digits = str(abs(value.numerator) * 10 ** places // value.denominator).rjust(places + 1, "0")
    return ("-" if value < 0 else "") + digits[:-places] + "." + digits[-places:]


def run_scenario(treasury: dict[str, Fraction], scenario: dict[str, Any], periods: int,
                 coverage_floor: Fraction, allow_synthetic: bool) -> dict[str, Any]:
    name = scenario.get("id")
    if not isinstance(name, str) or not _ID.match(name):
        raise Refused("STRESS_SCENARIO_IDENTITY", "every scenario has an id", "give the scenario an id")
    missing = [d for d in DIMENSIONS if not isinstance(scenario.get(d), dict)]
    if missing:
        raise Refused("REQUIRED_STRESS_DIMENSION_MISSING", "the scenario declares all five S5_STRESS dimensions",
                      "declare " + ", ".join(missing), scenario=name, missing=missing)
    v = {key: _input(scenario[dim], key, f"{name}.{dim}", allow_synthetic)
         for dim, keys in DIMENSION_INPUTS.items() for key in keys}
    reserve, claims = treasury["treasury_value"], treasury["redeemable_claims"]
    volatile = treasury["volatile_share"]
    failures: list[dict[str, Any]] = []
    trajectory = []
    for period in range(1, periods + 1):
        shock = min(Fraction(1), v["price_drop_per_period"] + v["sold_share_per_period"] * v["price_impact_per_unit_sold"])
        reserve -= reserve * volatile * shock
        redeemed = claims * v["redemption_rate_per_period"]
        claims -= redeemed
        reserve += treasury["revenue_per_period"] - redeemed - v["rewards_per_period"] - v["operating_cost_per_period"]
        runway = reserve / v["operating_cost_per_period"] if v["operating_cost_per_period"] else None
        coverage = reserve / claims if claims else None
        trajectory.append({"period": period, "treasury": _number(reserve), "redeemable_claims": _number(claims),
                           "coverage": None if coverage is None else _number(coverage),
                           "runway_periods": None if runway is None else _number(runway)})
        checks = (("solvency", reserve >= 0),
                  ("coverage", coverage is None or coverage >= coverage_floor),
                  ("service_continuity", runway is None or runway >= v["minimum_runway_periods"]))
        for predicate, ok in checks:
            if not ok and predicate not in {f["failed_predicate"] for f in failures}:
                failures.append({"failed_predicate": predicate, "first_failing_period": period})
    return {"scenario": name, "disposition": "DENY" if failures else "ALLOW", "failures": failures,
            "trajectory": trajectory}


def evaluate(document: Any) -> dict[str, Any]:
    if not isinstance(document, dict) or document.get("schema") != SCHEMA:
        raise Refused("STRESS_SCHEMA_MISMATCH", f"schema == {SCHEMA}", "supply a scenario file of the declared schema")
    if document.get("benchmark_id") != BENCHMARK_ID:
        raise Refused("STRESS_BENCHMARK_IDENTITY", f"benchmark_id == {BENCHMARK_ID}", "bind the file to S5_STRESS")
    fixture = document.get("fixture") is True
    periods = document.get("periods")
    if isinstance(periods, bool) or not isinstance(periods, int) or not 1 <= periods <= MAX_PERIODS:
        raise Refused("STRESS_INPUT_OUT_OF_RANGE", f"periods is an integer in [1, {MAX_PERIODS}]", "set periods")
    treasury = {key: _input(document.get("treasury"), key, "treasury", fixture) for key in TREASURY_INPUTS}
    floor = _input(document.get("treasury"), "coverage_floor", "treasury", fixture)
    scenarios = document.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise Refused("STRESS_SCENARIOS_MISSING", "at least one scenario is declared", "declare scenarios")
    results = [run_scenario(treasury, s if isinstance(s, dict) else {}, periods, floor, fixture) for s in scenarios]
    ids = [r["scenario"] for r in results]
    if len(ids) != len(set(ids)):
        raise Refused("STRESS_SCENARIO_IDENTITY", "scenario ids are unique", "rename the duplicate scenario")
    result = {
        "schema": RESULT_SCHEMA, "benchmark_id": BENCHMARK_ID, "goal_task_id": GOAL, "disposition": "ALLOW",
        "fixture": fixture, "periods": periods, "scenarios": results,
        "evidence_class": "FIXTURE_NOT_EVIDENCE" if fixture else "SOURCE_IMPLEMENTED", "benchmark_completion_granted": False,
        "realism_owner_accepted": False, "authority_effect": "NONE",
    }
    failing = [(r["scenario"], f) for r in results for f in r["failures"]]
    if failing:
        scenario, first = failing[0]
        result.update({
            "disposition": "DENY", "failure_code": f"S5_STRESS_{first['failed_predicate'].upper()}_NOT_MET",
            "failed_predicate": first["failed_predicate"],
            "required_evidence_or_repair": (f"scenario {scenario} fails {first['failed_predicate']} from period "
                                            f"{first['first_failing_period']}; supply treasury or scenario inputs under which "
                                            "every predicate holds in every period (the test never relaxes a predicate)"),
            "retry_entrypoint": RETRY, "owning_existing_goal": GOAL,
            "next_attempt": "after the owner supplies accepted inputs under which every scenario holds",
            "evidence": {"scenario": scenario, "first_failing_period": first["first_failing_period"],
                         "failing": [{"scenario": s, **f} for s, f in failing]},
        })
    return result


def render(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("scenarios", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        result = evaluate(json.loads(args.scenarios.read_text(encoding="utf-8")))
    except Refused as refusal:
        print(json.dumps(refusal.result, indent=2, sort_keys=True))
        return 1
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps(Refused("STRESS_SCHEMA_MISMATCH", "scenario file is readable JSON", "supply readable JSON",
                                 detail=f"{type(exc).__name__}: {exc}").result, indent=2, sort_keys=True))
        return 1
    text = render(result)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0 if result["disposition"] == "ALLOW" else 2


if __name__ == "__main__":
    raise SystemExit(main())
