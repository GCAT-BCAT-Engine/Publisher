"""Publisher-owned public-safe export of economic roadmap benchmark evidence.

Converts benchmark-bound governed closure records into the
``stegverse.economic-roadmap-evidence/v1`` projection that the Site read-only
subgoal projector consumes (``StegVerse-Labs/Site:scripts/project_economic_roadmap_subgoals.py
--evidence``).

Each input record binds one benchmark predicate to the governed transition that
proves it and carries, verbatim under ``master_records_closure``, the result of the
existing closure path (``StegVerse-org/LLM-adapter:llm_adapter/wiki_publication_master_records.py``
``record_governed_publication_closure``): ``state``, ``master_record_ref``, both receipt
digests, ``reconstruction_status`` and ``required_evidence_validation_status``. The
input schema is Publisher-owned; Master Records defines only the closure fields.

This module does not query Master Records, execute Interlock/InTr, authenticate a
receipt, publish, or promote any benchmark. It only validates caller-supplied
closure records fail-closed and strips everything that is not public-safe. A record
that does not prove its own closure predicates is refused with an exact failed
predicate instead of being exported. The Site can at most mark a fully evidenced
benchmark ELIGIBLE_FOR_PUBLISHER_GOVERNED_REVIEW; completion stays governed.
"""
from __future__ import annotations

import json
import re
from typing import Any, Iterable, Mapping

TASK_ID = "ECOSYSTEM-ECONOMIC-WHITEPAPER-GATED-ROADMAP-001"
EVIDENCE_SCHEMA = "stegverse.economic-roadmap-evidence/v1"
INPUT_SCHEMA = "stegverse.publisher.economic-benchmark-closure-input/v1"
# A committed request is the on-request entry point: the export runs because a request
# file exists on main, never because a receiver or interface is reachable.
REQUEST_SCHEMA = "stegverse.publisher.economic-evidence-export-request/v1"
REQUEST_DIR = ".stegverse/economic-evidence-export-requests"
EVIDENCE_SOURCE = "PUBLISHER_GOVERNED_PROJECTION"
# Benchmark identity pinned to StegVerse-Labs/Site:data/economy/public-release-benchmarks.v1.json.
BENCHMARK_IDS = (
    "S1_NATIVE_KV", "S1_MYKV_AI", "S1_CHATGPT", "S1_CLAUDE", "S1_FREE_COST",
    "S2_CONSENT", "S2_PRIVACY", "S3_PURCHASE", "S3_PROVEN_VALUE",
    "S4_COST", "S4_SETTLEMENT", "S4_REWARDS", "S5_LEGAL", "S5_STRESS",
    "S6_FEDERATION", "S6_PURCHASING_POWER",
)
# Exact producer identity and boundary of StegVerse-org/LLM-adapter
# record_governed_publication_closure on success (CLOSURE_SCHEMA there).
CLOSURE_SCHEMA = "stegverse.external-framework-wiki-publication-governed-closure/v1"
CLOSURE_AUTHORITY_EFFECT = "NONE_DOWNSTREAM_RECORDING_ONLY"
NON_ALLOW = {"DENY", "FAIL_CLOSED"}
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_PREDICATE = re.compile(r"^[A-Za-z0-9_]{1,128}$")
_REF = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://[^\s]{1,500}$")
# References into private state must never reach the public projection.
_PRIVATE_REF_SCHEMES = ("mykv://", "skap://", "tvc://", "secret://", "wallet://")


class EconomicRoadmapEvidenceError(ValueError):
    pass


def _refusal(record: Any, failed_predicate: str) -> dict[str, Any]:
    row = record if isinstance(record, Mapping) else {}
    return {
        "benchmark_id": row.get("benchmark_id") if isinstance(row.get("benchmark_id"), str) else None,
        "predicate": row.get("predicate") if isinstance(row.get("predicate"), str) else None,
        "disposition": "FAIL_CLOSED",
        "failed_predicate": failed_predicate,
    }


def _public_ref(value: Any) -> str | None:
    if not isinstance(value, str) or not _REF.match(value):
        return None
    if value.lower().startswith(_PRIVATE_REF_SCHEMES):
        return None
    # A public reference must not carry embedded URL credentials or control bytes.
    from urllib.parse import urlsplit
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        return None
    try:
        parsed = urlsplit(value)
    except ValueError:
        return None
    if parsed.username is not None or parsed.password is not None:
        return None
    # Public references must not be executable URLs or malformed HTTP targets.
    if parsed.scheme.lower() in {"javascript", "data", "file", "vbscript"}:
        return None
    if parsed.scheme.lower() in {"http", "https"} and not parsed.hostname:
        return None
    return value


def _validate(record: Any) -> tuple[str, str, dict[str, Any]] | dict[str, Any]:
    """Return (benchmark_id, predicate, public_entry) or a refusal row."""
    if not isinstance(record, Mapping):
        return _refusal(record, "malformed_closure_record")
    if record.get("schema") != INPUT_SCHEMA:
        return _refusal(record, "input_schema")
    if record.get("goal_task_id") != TASK_ID:
        return _refusal(record, "goal_task_identity")
    benchmark_id = record.get("benchmark_id")
    if benchmark_id not in BENCHMARK_IDS:
        return _refusal(record, "correct_benchmark_identity")
    predicate = record.get("predicate")
    if not isinstance(predicate, str) or not _PREDICATE.match(predicate):
        return _refusal(record, "predicate_identity")
    evidence_ref = _public_ref(record.get("evidence_ref"))
    if evidence_ref is None:
        return _refusal(record, "public_safe_evidence_ref")

    disposition = record.get("disposition")
    if disposition in NON_ALLOW:
        failed = record.get("failed_predicate")
        if not isinstance(failed, str) or not _PREDICATE.match(failed):
            return _refusal(record, "non_allow_failed_predicate_required")
        return benchmark_id, predicate, {
            "disposition": disposition, "failed_predicate": failed, "evidence_ref": evidence_ref,
        }
    if disposition != "ALLOW":
        return _refusal(record, "governed_disposition_required")
    if record.get("synthetic") is not False:
        return _refusal(record, "evidence_not_declared_non_synthetic")
    closure = record.get("master_records_closure")
    if not isinstance(closure, Mapping):
        return _refusal(record, "master_records_closure_required")
    if closure.get("schema") != CLOSURE_SCHEMA:
        return _refusal(record, "master_records_closure_schema")
    if closure.get("state") != "RECORDED":
        return _refusal(record, "master_records_state_RECORDED")
    # Master Records records downstream; a closure claiming more than that is refused.
    if (closure.get("authority_effect") != CLOSURE_AUTHORITY_EFFECT
            or closure.get("gates_publication") is not False
            or closure.get("master_records_grants_transition_authority") is not False):
        return _refusal(record, "master_records_closure_authority_boundary")
    if closure.get("reconstruction_status") != "PASS":
        return _refusal(record, "reconstruction_PASS")
    if closure.get("required_evidence_validation_status") != "PASS":
        return _refusal(record, "required_evidence_validation_PASS")
    receipt = closure.get("receipt_sha256")
    if not isinstance(receipt, str) or not _DIGEST.match(receipt) or receipt != closure.get("reconstructed_receipt_sha256"):
        return _refusal(record, "exact_receipt_digest_equality")
    if _public_ref(closure.get("master_record_ref")) is None:
        return _refusal(record, "master_record_ref")
    if closure["master_record_ref"] == evidence_ref:
        return _refusal(record, "independent_master_record_ref")
    if _public_ref(record.get("organization_receipt_ref")) is None:
        return _refusal(record, "organization_receipt_ref")
    if record["organization_receipt_ref"] == evidence_ref:
        return _refusal(record, "independent_organization_receipt_ref")
    if record["organization_receipt_ref"] == closure["master_record_ref"]:
        return _refusal(record, "independent_organization_master_record_refs")
    return benchmark_id, predicate, {
        "evidence_class": "MASTER_RECORDS_VERIFIED",
        "evidence_ref": evidence_ref,
        "benchmark_id": benchmark_id,
        "synthetic": False,
        "master_records_state": "RECORDED",
        "reconstruction_status": "PASS",
        "required_evidence_validation_status": "PASS",
        "receipt_sha256": receipt,
        "reconstructed_receipt_sha256": receipt,
        "organization_receipt_ref": record["organization_receipt_ref"],
    }


def export(records: Iterable[Any]) -> dict[str, Any]:
    """Build the public-safe evidence projection; never grants completion."""
    if isinstance(records, (str, bytes, Mapping)):
        raise EconomicRoadmapEvidenceError("closure_records_must_be_a_list")
    accepted: dict[tuple[str, str], list[tuple[Any, dict[str, Any]]]] = {}
    refused: list[dict[str, Any]] = []
    for record in records:
        result = _validate(record)
        if isinstance(result, dict):
            refused.append(result)
            continue
        benchmark_id, predicate, entry = result
        accepted.setdefault((benchmark_id, predicate), []).append((record, entry))
    benchmarks: dict[str, dict[str, Any]] = {}
    for (benchmark_id, predicate), rows in sorted(accepted.items()):
        if len(rows) > 1:
            # Duplicate or conflicting evidence for one predicate is never resolved here.
            refused.extend(_refusal(record, "duplicate_predicate_evidence") for record, _ in rows)
            continue
        benchmarks.setdefault(benchmark_id, {})[predicate] = rows[0][1]
    return {
        "schema": EVIDENCE_SCHEMA,
        "source": EVIDENCE_SOURCE,
        "goal_task_id": TASK_ID,
        "authority_effect": "NONE",
        "publication_executed": False,
        "benchmark_completion_granted": False,
        "readback_authenticated_by_this_module": False,
        "benchmarks": benchmarks,
        "refused": refused,
    }


def _request_refusal(name: str, failed_predicate: str) -> dict[str, Any]:
    return {"benchmark_id": None, "predicate": None, "request": name,
            "disposition": "FAIL_CLOSED", "failed_predicate": failed_predicate}


def materialize(request_dir: Any) -> dict[str, Any]:
    """Export the closure records named by every committed request in ``request_dir``.

    A request file that is not a well-formed request for this goal is refused with an
    exact failed predicate; it never blocks the other requests. No request yields the
    empty projection.
    """
    from pathlib import Path

    records: list[Any] = []
    refused: list[dict[str, Any]] = []
    directory = Path(request_dir)
    for path in sorted(directory.glob("*.json")) if directory.is_dir() else []:
        try:
            request = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            refused.append(_request_refusal(path.name, "request_json"))
            continue
        if not isinstance(request, Mapping) or request.get("schema") != REQUEST_SCHEMA:
            refused.append(_request_refusal(path.name, "request_schema"))
            continue
        if request.get("goal_task_id") != TASK_ID:
            refused.append(_request_refusal(path.name, "request_goal_task_identity"))
            continue
        if not isinstance(request.get("records"), list):
            refused.append(_request_refusal(path.name, "request_records_list"))
            continue
        records.extend(request["records"])
    projection = export(records)
    projection["refused"] = refused + projection["refused"]
    return projection


def render(projection: Mapping[str, Any]) -> str:
    return json.dumps(projection, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Export public-safe economic roadmap evidence")
    parser.add_argument("records", nargs="?", type=Path, help="JSON list of benchmark closure input records")
    parser.add_argument("--requests", type=Path, help=f"directory of committed export requests (e.g. {REQUEST_DIR})")
    parser.add_argument("--write", type=Path, help="write the projection to this path instead of stdout")
    args = parser.parse_args(argv)
    if args.requests is not None and args.records is not None:
        parser.error("pass either records or --requests, not both")
    if args.requests is not None:
        projection = materialize(args.requests)
    else:
        projection = export(json.loads(args.records.read_text(encoding="utf-8")) if args.records else [])
    if args.write is not None:
        args.write.write_text(render(projection), encoding="utf-8")
    else:
        print(json.dumps(projection, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
