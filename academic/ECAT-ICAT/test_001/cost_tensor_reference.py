#!/usr/bin/env python3
"""
StegVerse Cost Tensor Reference Evaluator
Version: 0.1.0-draft

Purpose:
  Minimal deterministic implementation for COST_TENSOR_TEST_SPEC_v0.1.0.

Done means:
  - Load JSON test vectors.
  - Evaluate ALLOW / DENY / FAIL_CLOSED.
  - Compute scalar cost.
  - Emit deterministic receipts.
  - Write:
      brain_reports/cost_tensor_test_report.json
      brain_reports/cost_tensor_receipts.jsonl

This is intentionally small. It is a reference gate, not a production runtime.
"""

from __future__ import annotations

import argparse
import json
import math
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


OUTCOME_ALLOW = "ALLOW"
OUTCOME_DENY = "DENY"
OUTCOME_FAIL_CLOSED = "FAIL_CLOSED"


@dataclass(frozen=True)
class Decision:
    outcome: str
    reason: str
    total_cost: Optional[float] = None
    receipt: Optional[Dict[str, Any]] = None


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def stable_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write("\n")


def is_missing(value: Any) -> bool:
    return value is None


def finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def nonnegative_cost(value: Any) -> bool:
    return finite_number(value) and float(value) >= 0.0


def fail_closed(reason: str) -> Decision:
    return Decision(OUTCOME_FAIL_CLOSED, reason)


def deny(reason: str, total_cost: Optional[float] = None) -> Decision:
    return Decision(OUTCOME_DENY, reason, total_cost)


def allow(reason: str, total_cost: float) -> Decision:
    return Decision(OUTCOME_ALLOW, reason, total_cost)


def transition_complete(transition: Dict[str, Any]) -> bool:
    required = [
        "entity_id",
        "data_id",
        "category",
        "pre_state_hash",
        "post_state_hash",
        "delta_hash",
        "policy_hash",
        "commit_time",
    ]
    if not transition.get("complete", False):
        return False
    return all(not is_missing(transition.get(key)) for key in required)


def evaluate_gcat(ctx: Dict[str, Any]) -> Optional[Decision]:
    gcat = ctx.get("gcat", {})
    if not gcat.get("available", False):
        return fail_closed("gcat_unknown")
    if not nonnegative_cost(gcat.get("cost")):
        return fail_closed("gcat_cost_invalid")
    if not gcat.get("pass", False):
        return deny("gcat_boundary_failure")
    return None


def evaluate_bcat(ctx: Dict[str, Any]) -> Optional[Decision]:
    bcat = ctx.get("bcat", {})
    if not bcat.get("available", False):
        return fail_closed("bcat_unknown")
    if not nonnegative_cost(bcat.get("cost")):
        return fail_closed("bcat_cost_invalid")
    if not bcat.get("pass", False):
        return deny("bcat_consequence_failure")
    return None


def evaluate_ecat(ctx: Dict[str, Any]) -> Optional[Decision]:
    ecat = ctx.get("ecat", {})
    if not ecat.get("available", False):
        return fail_closed("ecat_unknown")
    if not nonnegative_cost(ecat.get("cost")):
        return fail_closed("ecat_cost_invalid")

    reputation = ecat.get("reputation")
    if is_missing(reputation):
        return fail_closed("ecat_reputation_unknown")
    if not finite_number(reputation) or not (0.0 <= float(reputation) <= 1.0):
        return fail_closed("ecat_reputation_invalid")
    if float(reputation) == 0.0:
        return fail_closed("ecat_reputation_null")

    r_min = ecat.get("r_min", 0.0)
    if not finite_number(r_min) or not (0.0 <= float(r_min) <= 1.0):
        return fail_closed("ecat_r_min_invalid")
    if float(reputation) < float(r_min):
        return deny("ecat_reputation_failure")

    stake_risk = ecat.get("stake_risk")
    stake_min = ecat.get("stake_min")
    if not finite_number(stake_risk) or float(stake_risk) < 0.0:
        return fail_closed("ecat_stake_invalid")
    if not finite_number(stake_min) or float(stake_min) < 0.0:
        return fail_closed("ecat_stake_min_invalid")
    if float(stake_risk) < float(stake_min):
        return deny("ecat_stake_failure")

    h = ecat.get("h")
    h_max = ecat.get("h_max")
    if h == "Infinity":
        return fail_closed("ecat_historical_impossible")
    if not finite_number(h) or float(h) < 0.0:
        return fail_closed("ecat_historical_invalid")
    if not finite_number(h_max) or float(h_max) < 0.0:
        return fail_closed("ecat_h_max_invalid")
    if float(h) > float(h_max):
        return deny("ecat_historical_anomaly")

    consent = ecat.get("consent")
    if consent is None:
        return fail_closed("consent_unavailable")
    if ecat.get("co_owner_rejected", False):
        return fail_closed("co_owner_rejected")
    if consent is not True:
        return fail_closed("consent_unavailable")

    if not ecat.get("pass", False):
        return deny("ecat_failure")
    return None


def evaluate_icat(ctx: Dict[str, Any]) -> Optional[Decision]:
    icat = ctx.get("icat", {})
    if not icat.get("available", False):
        return fail_closed("icat_unknown")
    if not nonnegative_cost(icat.get("cost")):
        return fail_closed("icat_cost_invalid")

    if icat.get("proof_score") is not None:
        proof_score = icat.get("proof_score")
        if not finite_number(proof_score) or not (0.0 <= float(proof_score) <= 1.0):
            return fail_closed("proof_score_invalid")

    if icat.get("proof_available") is False:
        return fail_closed("proof_unavailable")
    if icat.get("proof_valid") is False:
        return deny("proof_invalid")

    if icat.get("witness_available") is False:
        return fail_closed("witness_unavailable")

    witness_score = icat.get("witness_score")
    witness_min = icat.get("witness_min", 0.0)
    if not finite_number(witness_score) or not (0.0 <= float(witness_score) <= 1.0):
        return fail_closed("witness_score_invalid")
    if not finite_number(witness_min) or not (0.0 <= float(witness_min) <= 1.0):
        return fail_closed("witness_min_invalid")

    independent = icat.get("independent")
    if independent is None:
        return fail_closed("witness_independence_unknown")
    if independent is False:
        return deny("witness_non_independent")

    if float(witness_score) < float(witness_min):
        return deny("witness_quorum_failure")

    n_valid = icat.get("n_valid")
    n_min = icat.get("n_min")
    if not isinstance(n_valid, int) or not isinstance(n_min, int) or n_valid < 0 or n_min < 0:
        return fail_closed("witness_count_invalid")
    if n_valid < n_min:
        return deny("witness_quorum_failure")

    if icat.get("conservation_available") is False:
        return fail_closed("conservation_unavailable")
    if icat.get("conservation_pass") is False:
        return deny("conservation_failure")

    if icat.get("inverse_available") is False:
        return fail_closed("inverse_unavailable")
    if icat.get("inverse_pass") is False:
        return deny("inverse_failure")

    if not icat.get("pass", False):
        return deny("icat_failure")
    return None


def build_receipt(ctx: Dict[str, Any], outcome: str, reason: str, total_cost: Optional[float]) -> Dict[str, Any]:
    transition = ctx["transition"]
    receipt = {
        "schema": "stegverse.cost_tensor.receipt.v1",
        "transition_id": ctx.get("test_id", "unknown"),
        "entity_id": transition.get("entity_id"),
        "data_id": transition.get("data_id"),
        "pre_state_hash": transition.get("pre_state_hash"),
        "post_state_hash": transition.get("post_state_hash"),
        "delta_hash": transition.get("delta_hash"),
        "policy_hash": transition.get("policy_hash"),
        "budget_id": ctx.get("budget", {}).get("budget_id", "test-budget"),
        "commit_time": transition.get("commit_time"),
        "gcat": {
            "pass": ctx.get("gcat", {}).get("pass"),
            "cost": ctx.get("gcat", {}).get("cost"),
            "basis_hash": stable_hash(ctx.get("gcat", {})),
        },
        "bcat": {
            "pass": ctx.get("bcat", {}).get("pass"),
            "cost": ctx.get("bcat", {}).get("cost"),
            "basis_hash": stable_hash(ctx.get("bcat", {})),
        },
        "ecat": {
            "pass": ctx.get("ecat", {}).get("pass"),
            "cost": ctx.get("ecat", {}).get("cost"),
            "basis_hash": stable_hash(ctx.get("ecat", {})),
        },
        "icat": {
            "pass": ctx.get("icat", {}).get("pass"),
            "cost": ctx.get("icat", {}).get("cost"),
            "basis_hash": stable_hash(ctx.get("icat", {})),
        },
        "total_cost": total_cost,
        "budget": ctx.get("budget", {}).get("amount"),
        "outcome": outcome,
        "reason": reason,
        "prev_receipt_hash": ctx.get("prev_receipt_hash", "GENESIS"),
        "signer": "cost_tensor_reference.py",
    }
    receipt["receipt_hash"] = stable_hash(receipt)
    return receipt


def evaluate_commit_admissibility(ctx: Dict[str, Any]) -> Decision:
    transition = ctx.get("transition", {})
    if not transition_complete(transition):
        decision = fail_closed("transition_object_incomplete")
        return attach_receipt_if_possible(ctx, decision)

    if transition.get("policy_hash") is None:
        decision = fail_closed("policy_unavailable")
        return attach_receipt_if_possible(ctx, decision)

    budget = ctx.get("budget", {})
    if not budget.get("available", False):
        decision = fail_closed("budget_unavailable")
        return attach_receipt_if_possible(ctx, decision)
    if not nonnegative_cost(budget.get("amount")):
        decision = fail_closed("budget_invalid")
        return attach_receipt_if_possible(ctx, decision)

    for evaluator in (evaluate_gcat, evaluate_bcat, evaluate_ecat, evaluate_icat):
        decision = evaluator(ctx)
        if decision is not None:
            return attach_receipt_if_possible(ctx, decision)

    total_cost = (
        float(ctx["gcat"]["cost"])
        + float(ctx["bcat"]["cost"])
        + float(ctx["ecat"]["cost"])
        + float(ctx["icat"]["cost"])
    )

    if total_cost > float(budget["amount"]):
        decision = deny("budget_exceeded", total_cost)
        return attach_receipt_if_possible(ctx, decision)

    decision = allow("cost_tensor_admissible", total_cost)
    return attach_receipt_if_possible(ctx, decision)


def attach_receipt_if_possible(ctx: Dict[str, Any], decision: Decision) -> Decision:
    receipt_cfg = ctx.get("receipt", {})
    if receipt_cfg.get("emit_ok", True) is False:
        if decision.outcome == OUTCOME_ALLOW:
            return Decision(OUTCOME_FAIL_CLOSED, "receipt_emission_failed", decision.total_cost, None)
        return Decision(decision.outcome, decision.reason, decision.total_cost, None)

    receipt = build_receipt(ctx, decision.outcome, decision.reason, decision.total_cost)
    return Decision(decision.outcome, decision.reason, decision.total_cost, receipt)


def check_expected(vector: Dict[str, Any], decision: Decision) -> Tuple[bool, List[str]]:
    expected = vector.get("expected", {})
    errors: List[str] = []

    if decision.outcome != expected.get("outcome"):
        errors.append(f"outcome expected {expected.get('outcome')} got {decision.outcome}")

    if expected.get("reason") is not None and decision.reason != expected.get("reason"):
        errors.append(f"reason expected {expected.get('reason')} got {decision.reason}")

    if expected.get("total_cost") is not None:
        if decision.total_cost is None:
            errors.append(f"total_cost expected {expected.get('total_cost')} got None")
        elif abs(float(decision.total_cost) - float(expected["total_cost"])) > 1e-9:
            errors.append(f"total_cost expected {expected.get('total_cost')} got {decision.total_cost}")

    if expected.get("receipt_valid") is True:
        if not decision.receipt:
            errors.append("receipt expected but missing")
        else:
            required = [
                "transition_id",
                "entity_id",
                "data_id",
                "pre_state_hash",
                "post_state_hash",
                "delta_hash",
                "policy_hash",
                "budget_id",
                "commit_time",
                "gcat",
                "bcat",
                "ecat",
                "icat",
                "total_cost",
                "budget",
                "outcome",
                "reason",
                "prev_receipt_hash",
                "receipt_hash",
                "signer",
            ]
            missing = [field for field in required if field not in decision.receipt]
            if missing:
                errors.append(f"receipt missing fields {missing}")

    return len(errors) == 0, errors


def run_vectors(vectors_path: Path, out_dir: Path) -> Dict[str, Any]:
    vector_files = sorted(vectors_path.glob("*.json"))
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    receipts = []

    for path in vector_files:
        vector = load_json(path)
        decision = evaluate_commit_admissibility(vector)
        passed, errors = check_expected(vector, decision)

        if decision.receipt is not None:
            receipts.append(decision.receipt)

        results.append(
            {
                "test_id": vector.get("test_id"),
                "name": vector.get("name"),
                "expected": vector.get("expected", {}).get("outcome"),
                "actual": decision.outcome,
                "reason_expected": vector.get("expected", {}).get("reason"),
                "reason_actual": decision.reason,
                "passed": passed,
                "errors": errors,
                "receipt_hash": decision.receipt.get("receipt_hash") if decision.receipt else None,
            }
        )

    report = {
        "schema": "stegverse.cost_tensor.test_report.v1",
        "seed": 42,
        "suite": "COST_TENSOR_TEST_SPEC_v0.1.0",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total": len(results),
            "passed": sum(1 for item in results if item["passed"]),
            "failed": sum(1 for item in results if not item["passed"]),
            "skipped": 0,
        },
        "results": results,
    }

    write_json(out_dir / "cost_tensor_test_report.json", report)

    with (out_dir / "cost_tensor_receipts.jsonl").open("w", encoding="utf-8") as f:
        for receipt in receipts:
            f.write(canonical_json(receipt) + "\n")

    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vectors", default="test_vectors", help="Directory containing JSON test vectors")
    parser.add_argument("--out", default="brain_reports", help="Output directory for reports")
    args = parser.parse_args()

    report = run_vectors(Path(args.vectors), Path(args.out))
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0 if report["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
