#!/usr/bin/env python3
"""Roadmap benchmark S2_PRIVACY: bounded result disclosure over inputs by reference.

S2_PRIVACY (StegVerse-Labs/Site:data/economy/public-release-benchmarks.v1.json) requires an
"authentic authorized result with independent privacy and purpose validation, no
raw-state leakage". Inputs follow tools/benchmark_input_reference.py (pinned ref + sha256,
caller bytes, nothing fetched).

Four predicates are evaluated here, over three required inputs: ``disclosed_result``
(``stegverse.bounded-disclosure-result.v1``), ``disclosure_policy``
(``stegverse.disclosure-policy.v1``) and ``authorization_record``
(``stegverse.disclosure-authorization.v1``):

* ``RESULT_FIELDS_WITHIN_DECLARED_PURPOSE``: every disclosed field is allowed by the
  policy, and the result, policy and authorization name the same purpose;
* ``NO_RAW_STATE_FIELDS``: no declared raw-state field name appears anywhere in a disclosed
  cell: neither as a top-level field nor as a key nested at any depth inside a field's value
  (objects and arrays are walked). Matching is by exact key name, the same as the policy's declared
  names; string values are not parsed as JSON, so the policy must not allow a field whose string value
  can carry serialized raw state. Nesting depth and node count are bounded; a value past the bound is
  refused FAIL_CLOSED rather than half-inspected;
* ``AGGREGATION_THRESHOLD``: every aggregate cell covers at least
  ``min_subjects_per_cell`` subjects (exact integers);
* ``RESULT_DIGEST_BOUND_TO_AUTHORIZATION``: the canonical digest of the disclosed result
  equals the authorization record's ``result_sha256``.

Two predicates cannot be decided on the ecosystem side and always end FAIL_CLOSED, naming
exactly what is missing:

* ``AUTHORIZED_RESULT_AUTHENTIC`` needs ``skap_execution_receipt``, the SKAP owner's receipt
  for an authorized execution over Interlock/InTr, plus a SKAP-defined verifier. This module
  does not verify SKAP authenticity;
* ``INDEPENDENT_VALIDATION`` needs ``independent_validator_policy``, the owner's decision on
  who validates independently of the producer, plus that validator's attestation.

So the possible answers today are DENY (a named buildable predicate fails) or FAIL_CLOSED
(missing input or owner decision). ALLOW becomes reachable only once SKAP and the owner
supply those. Every non-ALLOW carries the six fields; nothing grants completion.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

sys.path.insert(0, str(Path(__file__).resolve().parent))
import benchmark_input_reference as ref  # noqa: E402

BENCHMARK_ID = "S2_PRIVACY"
MANIFEST_SCHEMA = "stegverse.s2-privacy-benchmark-inputs.v1"
RESULT_IN_SCHEMA = "stegverse.bounded-disclosure-result.v1"
POLICY_SCHEMA = "stegverse.disclosure-policy.v1"
AUTH_SCHEMA = "stegverse.disclosure-authorization.v1"
RESULT_SCHEMA = "stegverse.s2-privacy-benchmark-result.v1"
RETRY = "python3 tools/s2_privacy_disclosure_check.py <manifest.json> --input NAME=PATH ..."
REQUIRED_INPUTS = ("disclosed_result", "disclosure_policy", "authorization_record")
BUILDABLE = ("RESULT_FIELDS_WITHIN_DECLARED_PURPOSE", "NO_RAW_STATE_FIELDS", "AGGREGATION_THRESHOLD",
             "RESULT_DIGEST_BOUND_TO_AUTHORIZATION")
OWNER_GATED = (
    ("AUTHORIZED_RESULT_AUTHENTIC", "skap_execution_receipt",
     "the SKAP owner's receipt for an authorized execution over Interlock/InTr, and a SKAP-defined verifier"),
    ("INDEPENDENT_VALIDATION", "independent_validator_policy",
     "the owner-authored policy naming the validator independent of the producer, and its attestation"),
)


def _invalid(predicate: str, repair: str, **evidence: Any) -> ref.Refused:
    return ref.Refused(ref.six(BENCHMARK_ID, RESULT_SCHEMA, RETRY, "FAIL_CLOSED", "INPUT_VALUE_INVALID", predicate, repair,
                               "after the named input is corrected", **evidence))


MAX_DEPTH, MAX_NODES = 64, 100000


def _raw_paths(value: Any, raw: set[str], path: str, budget: list[int], depth: int = 0) -> list[str]:
    """Paths of every key in ``raw`` nested inside ``value`` (objects and arrays, bounded)."""
    budget[0] -= 1
    if depth > MAX_DEPTH or budget[0] < 0:
        raise _invalid(f"disclosed values nest at most {MAX_DEPTH} levels and {MAX_NODES} nodes",
                       "disclose a bounded result", path=path)
    found: list[str] = []
    if isinstance(value, Mapping):
        for key, inner in value.items():
            here = f"{path}.{key}"
            if key in raw:
                found.append(here)
            found += _raw_paths(inner, raw, here, budget, depth + 1)
    elif isinstance(value, list):
        for i, inner in enumerate(value):
            found += _raw_paths(inner, raw, f"{path}[{i}]", budget, depth + 1)
    return found


def check(result: Any, policy: Any, authorization: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(result, Mapping) or result.get("schema") != RESULT_IN_SCHEMA or not isinstance(result.get("cells"), list):
        raise _invalid(f"disclosed_result schema == {RESULT_IN_SCHEMA} with a cells list", "supply the disclosed result")
    if not isinstance(policy, Mapping) or policy.get("schema") != POLICY_SCHEMA:
        raise _invalid(f"disclosure_policy schema == {POLICY_SCHEMA}", "supply the disclosure policy")
    if not isinstance(authorization, Mapping) or authorization.get("schema") != AUTH_SCHEMA:
        raise _invalid(f"authorization_record schema == {AUTH_SCHEMA}", "supply the authorization record")
    allowed, raw = policy.get("allowed_fields"), policy.get("raw_state_fields")
    k = policy.get("min_subjects_per_cell")
    if (not isinstance(allowed, list) or not isinstance(raw, list) or isinstance(k, bool) or not isinstance(k, int) or k < 1
            or not all(isinstance(x, str) for x in allowed + raw)):
        raise _invalid("allowed_fields and raw_state_fields are lists of strings and min_subjects_per_cell >= 1",
                       "fix the policy")
    for name, doc in (("disclosed_result", result), ("disclosure_policy", policy), ("authorization_record", authorization)):
        if not isinstance(doc.get("purpose"), str) or not doc["purpose"]:
            raise _invalid(f"{name}.purpose is a non-empty string", f"declare {name}.purpose as a string", input=name)
    fields: set[str] = set()
    small: list[int] = []
    nested: list[str] = []
    budget = [MAX_NODES]
    for index, cell in enumerate(result["cells"]):
        values = cell.get("fields") if isinstance(cell, Mapping) else None
        count = cell.get("subject_count") if isinstance(cell, Mapping) else None
        if not isinstance(values, Mapping) or isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise _invalid("every cell has a fields object and an integer subject_count", "fix the result cells")
        fields.update(values)
        for name, value in values.items():
            nested += _raw_paths(value, set(raw), f"cells[{index}].fields.{name}", budget)
        if count < k:
            small.append(index)
    purposes = {result["purpose"], policy["purpose"], authorization["purpose"]}
    extra = sorted(fields - set(allowed))
    leaked = sorted(fields & set(raw))
    digest = ref.canonical_sha256(result)
    return {
        "RESULT_FIELDS_WITHIN_DECLARED_PURPOSE": {"holds": not extra and len(purposes) == 1,
                                                  "fields_outside_purpose": extra, "purpose_consistent": len(purposes) == 1},
        "NO_RAW_STATE_FIELDS": {"holds": not leaked and not nested, "raw_state_fields_disclosed": leaked,
                                "raw_state_keys_nested": nested},
        "AGGREGATION_THRESHOLD": {"holds": bool(result["cells"]) and not small, "min_subjects_per_cell": k,
                                  "cells_below_threshold": small},
        "RESULT_DIGEST_BOUND_TO_AUTHORIZATION": {"holds": authorization.get("result_sha256") == digest, "result_sha256": digest},
    }


def evaluate(manifest: Any, supplied: Mapping[str, bytes]) -> dict[str, Any]:
    inputs = ref.verified_inputs(manifest, supplied, manifest_schema=MANIFEST_SCHEMA, benchmark_id=BENCHMARK_ID,
                                 required=REQUIRED_INPUTS, result_schema=RESULT_SCHEMA, retry=RETRY)
    checks = check(inputs["disclosed_result"], inputs["disclosure_policy"], inputs["authorization_record"])
    declared = manifest.get("inputs") if isinstance(manifest.get("inputs"), Mapping) else {}
    for predicate, name, need in OWNER_GATED:
        checks[predicate] = {"holds": False, "decidable_here": False, "needs": need,
                             "input_supplied": name in declared and name in supplied}
    fixture = manifest.get("fixture") is True
    body = {"predicates": checks, "fixture": fixture,
            "evidence_class": "FIXTURE_NOT_EVIDENCE" if fixture else "SOURCE_IMPLEMENTED",
            "inputs": {name: dict(declared[name]) for name in REQUIRED_INPUTS}}
    failed = [p for p in BUILDABLE if not checks[p]["holds"]]
    if failed:
        result = ref.six(BENCHMARK_ID, RESULT_SCHEMA, RETRY, "DENY", f"S2_PRIVACY_{failed[0]}_NOT_MET", failed[0],
                         "supply a result, policy and authorization under which the named predicate holds",
                         "after the producer supplies a corrected disclosure", failed_predicates=failed)
    else:
        predicate, name, need = next(((p, n, d) for p, n, d in OWNER_GATED if not checks[p]["input_supplied"]), OWNER_GATED[0])
        if not checks[predicate]["input_supplied"]:
            result = ref.six(BENCHMARK_ID, RESULT_SCHEMA, RETRY, "FAIL_CLOSED", "INPUT_NOT_SUPPLIED", predicate,
                             f"supply {name}: {need}", f"after {name} exists", input=name)
        else:
            result = ref.six(BENCHMARK_ID, RESULT_SCHEMA, RETRY, "FAIL_CLOSED", "OWNER_VERIFIER_UNDEFINED", predicate,
                             f"the owner of {name} defines how it is verified; this module does not judge it",
                             "after the SKAP owner and the owner define the verifiers", input=name)
    result.update(body)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--input", action="append", default=[], metavar="NAME=PATH")
    args = parser.parse_args(argv)
    try:
        result = evaluate(json.loads(args.manifest.read_text(encoding="utf-8")), ref.read_cli_inputs(args.input))
    except ref.Refused as refusal:
        result = refusal.result
    except (OSError, ValueError, TypeError) as exc:
        result = ref.six(BENCHMARK_ID, RESULT_SCHEMA, RETRY, "FAIL_CLOSED", "INPUT_MANIFEST_SCHEMA",
                         "manifest and inputs are readable", "supply readable files", "after the files are readable",
                         detail=f"{type(exc).__name__}: {exc}")
    print(json.dumps(result, indent=2, sort_keys=True))
    return {"ALLOW": 0, "DENY": 2}.get(result["disposition"], 1)


if __name__ == "__main__":
    raise SystemExit(main())
