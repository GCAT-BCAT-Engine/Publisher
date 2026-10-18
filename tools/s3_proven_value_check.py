#!/usr/bin/env python3
"""Roadmap benchmark S3_PROVEN_VALUE: measured human service benefit over attributed orders.

S3_PROVEN_VALUE (StegVerse-Labs/Site:data/economy/public-release-benchmarks.v1.json)
requires a "comparative result [that] proves a human-supplied service added verifiable
value, without fabricated orders". Two inputs, supplied by reference
(tools/benchmark_input_reference.py):

* ``service_outcomes`` (``stegverse.service-outcomes.v1``): one row per order with
  ``order_id``, ``arm`` (``HUMAN_SERVICE`` or ``BASELINE``), ``value`` (exact decimal string
  in the declared metric), ``receipt_ref`` and ``receipt_sha256``. These are the real
  S3_PURCHASE outcomes; without them the answer is FAIL_CLOSED ``INPUT_NOT_SUPPLIED``;
* ``study_policy`` (``stegverse.s3-value-study-policy.v1``): ``metric``,
  ``min_orders_per_arm`` and ``min_effect`` (the smallest mean difference that counts).

Predicates, exact (``fractions.Fraction``):

* ``ORDERS_ATTRIBUTABLE``: every order carries a governed receipt reference
  (``org-ledger://``, ``master-records://`` or ``https://``) and a 64-hex receipt digest;
* ``NO_FABRICATED_ORDERS``: the outcome set is declared non-synthetic (unless the
  manifest is a fixture) and no order id or receipt digest repeats;
* ``SAMPLE_SUFFICIENT``: each arm has at least ``min_orders_per_arm`` orders;
* ``VALUE_ADDED``: mean(HUMAN_SERVICE) − mean(BASELINE) ≥ ``min_effect``.

ALLOW, DENY (named predicate) or FAIL_CLOSED, each non-ALLOW with the six fields. Fixture
output is never evidence; nothing here grants completion or authority.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

sys.path.insert(0, str(Path(__file__).resolve().parent))
import benchmark_input_reference as ref  # noqa: E402

BENCHMARK_ID = "S3_PROVEN_VALUE"
MANIFEST_SCHEMA = "stegverse.s3-proven-value-benchmark-inputs.v1"
OUTCOMES_SCHEMA = "stegverse.service-outcomes.v1"
POLICY_SCHEMA = "stegverse.s3-value-study-policy.v1"
RESULT_SCHEMA = "stegverse.s3-proven-value-benchmark-result.v1"
RETRY = "python3 tools/s3_proven_value_check.py <manifest.json> --input NAME=PATH ..."
REQUIRED_INPUTS = ("service_outcomes", "study_policy")
ARMS = ("HUMAN_SERVICE", "BASELINE")
PREDICATES = ("ORDERS_ATTRIBUTABLE", "NO_FABRICATED_ORDERS", "SAMPLE_SUFFICIENT", "VALUE_ADDED")
_RECEIPT = re.compile(r"^(org-ledger://|master-records://|https://)\S{1,500}$")
_SHA = re.compile(r"^[0-9a-f]{64}$")


def _exact(value: Any) -> Fraction | None:
    if not isinstance(value, str):
        return None
    try:
        d = Decimal(value)
    except InvalidOperation:
        return None
    return Fraction(d) if d.is_finite() else None


def _text(x: Fraction) -> str:
    return str(x.numerator) if x.denominator == 1 else str(Decimal(x.numerator) / Decimal(x.denominator))


def _invalid(predicate: str, repair: str, **evidence: Any) -> ref.Refused:
    return ref.Refused(ref.six(BENCHMARK_ID, RESULT_SCHEMA, RETRY, "FAIL_CLOSED", "INPUT_VALUE_INVALID", predicate, repair,
                               "after the named input is corrected", **evidence))


def check(outcomes: Any, policy: Any, fixture: bool) -> dict[str, dict[str, Any]]:
    if not isinstance(outcomes, Mapping) or outcomes.get("schema") != OUTCOMES_SCHEMA or not isinstance(outcomes.get("orders"), list):
        raise _invalid(f"service_outcomes schema == {OUTCOMES_SCHEMA} with an orders list", "supply service outcomes")
    if not isinstance(policy, Mapping) or policy.get("schema") != POLICY_SCHEMA:
        raise _invalid(f"study_policy schema == {POLICY_SCHEMA}", "supply the study policy")
    minimum = policy.get("min_orders_per_arm")
    effect = _exact(policy.get("min_effect"))
    if isinstance(minimum, bool) or not isinstance(minimum, int) or minimum < 1 or effect is None or effect < 0:
        raise _invalid("min_orders_per_arm >= 1 and min_effect a non-negative decimal string", "fix the study policy")
    if outcomes.get("metric") != policy.get("metric") or not policy.get("metric"):
        raise _invalid("service_outcomes.metric == study_policy.metric", "compare outcomes in the declared metric")
    orders = outcomes["orders"]
    values: dict[str, list[Fraction]] = {arm: [] for arm in ARMS}
    unattributed, ids, digests = 0, [], []
    for row in orders:
        if not isinstance(row, Mapping) or row.get("arm") not in ARMS or _exact(row.get("value")) is None:
            raise _invalid("every order has an arm in HUMAN_SERVICE/BASELINE and an exact decimal value", "fix the order rows")
        values[row["arm"]].append(_exact(row["value"]))
        ids.append(row.get("order_id"))
        digests.append(row.get("receipt_sha256"))
        if not (isinstance(row.get("receipt_ref"), str) and _RECEIPT.match(row["receipt_ref"])
                and isinstance(row.get("receipt_sha256"), str) and _SHA.match(row["receipt_sha256"])
                and isinstance(row.get("order_id"), str) and row["order_id"]):
            unattributed += 1
    out: dict[str, dict[str, Any]] = {}
    out["ORDERS_ATTRIBUTABLE"] = {"holds": bool(orders) and unattributed == 0, "unattributed_orders": unattributed}
    duplicates = (len(ids) - len(set(ids))) + (len(digests) - len(set(digests)))
    declared_real = outcomes.get("synthetic") is False
    out["NO_FABRICATED_ORDERS"] = {"holds": (declared_real or fixture) and duplicates == 0,
                                   "declared_non_synthetic": declared_real, "repeated_ids_or_receipts": duplicates}
    counts = {arm: len(values[arm]) for arm in ARMS}
    out["SAMPLE_SUFFICIENT"] = {"holds": all(n >= minimum for n in counts.values()), "orders_per_arm": counts,
                                "min_orders_per_arm": minimum}
    if all(counts.values()):
        means = {arm: sum(values[arm], Fraction(0)) / counts[arm] for arm in ARMS}
        diff = means["HUMAN_SERVICE"] - means["BASELINE"]
        out["VALUE_ADDED"] = {"holds": diff >= effect, "mean_human_service": _text(means["HUMAN_SERVICE"]),
                              "mean_baseline": _text(means["BASELINE"]), "difference": _text(diff), "min_effect": _text(effect)}
    else:
        out["VALUE_ADDED"] = {"holds": False, "reason": "an arm has no orders"}
    return out


def evaluate(manifest: Any, supplied: Mapping[str, bytes]) -> dict[str, Any]:
    inputs = ref.verified_inputs(manifest, supplied, manifest_schema=MANIFEST_SCHEMA, benchmark_id=BENCHMARK_ID,
                                 required=REQUIRED_INPUTS, result_schema=RESULT_SCHEMA, retry=RETRY)
    fixture = manifest.get("fixture") is True
    checks = check(inputs["service_outcomes"], inputs["study_policy"], fixture)
    body = {"predicates": checks, "fixture": fixture,
            "evidence_class": "FIXTURE_NOT_EVIDENCE" if fixture else "SOURCE_IMPLEMENTED",
            "inputs": {name: dict(manifest["inputs"][name]) for name in REQUIRED_INPUTS}}
    failed = [p for p in PREDICATES if not checks[p]["holds"]]
    if failed:
        result = ref.six(BENCHMARK_ID, RESULT_SCHEMA, RETRY, "DENY", f"S3_PROVEN_VALUE_{failed[0]}_NOT_MET", failed[0],
                         "supply outcomes under which the named predicate holds; the evaluator never relaxes a predicate",
                         "after real S3_PURCHASE outcomes exist", failed_predicates=failed)
        result.update(body)
        return result
    return {"schema": RESULT_SCHEMA, "benchmark_id": BENCHMARK_ID, "disposition": "ALLOW",
            "authority": dict(ref.NO_AUTHORITY), **body}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--input", action="append", default=[], metavar="NAME=PATH")
    args = parser.parse_args(argv)
    try:
        result = evaluate(json.loads(args.manifest.read_text(encoding="utf-8")), ref.read_cli_inputs(args.input))
    except ref.Refused as refusal:
        result = refusal.result
    except (OSError, ValueError) as exc:
        result = ref.six(BENCHMARK_ID, RESULT_SCHEMA, RETRY, "FAIL_CLOSED", "INPUT_MANIFEST_SCHEMA",
                         "manifest and inputs are readable", "supply readable files", "after the files are readable",
                         detail=f"{type(exc).__name__}: {exc}")
    print(json.dumps(result, indent=2, sort_keys=True))
    return {"ALLOW": 0, "DENY": 2}.get(result["disposition"], 1)


if __name__ == "__main__":
    raise SystemExit(main())
