"""Benchmark inputs supplied by reference: pinned ref + sha256, caller-supplied bytes.

Shared by the roadmap benchmark evaluators in tools/. It follows the same input
contract as StegVerse-org/StegVerse-SDK:stegverse/s4_cost_benchmark.py (S4_COST): every
input is named ``owner/repo:path@<40-hex revision>`` with its ``sha256``, the caller
supplies the bytes, nothing is fetched, and a missing input is FAIL_CLOSED
``INPUT_NOT_SUPPLIED`` naming it. Refusals carry the six standard fields. Stdlib only.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping, Sequence

GOAL = "ECOSYSTEM-ECONOMIC-WHITEPAPER-GATED-ROADMAP-001"
_REF = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+:[^@\s]+@[0-9a-f]{40}$")
_SHA = re.compile(r"^[0-9a-f]{64}$")
NO_AUTHORITY = {"benchmark_completion_granted": False, "authority_effect": "NONE"}


def six(benchmark_id: str, result_schema: str, retry: str, disposition: str, code: str, predicate: str,
        repair: str, next_attempt: str, **evidence: Any) -> dict[str, Any]:
    return {"schema": result_schema, "benchmark_id": benchmark_id, "disposition": disposition,
            "failure_code": code, "failed_predicate": predicate, "required_evidence_or_repair": repair,
            "retry_entrypoint": retry, "owning_existing_goal": GOAL, "next_attempt": next_attempt,
            "evidence": evidence, "authority": dict(NO_AUTHORITY)}


class Refused(Exception):
    def __init__(self, result: dict[str, Any]) -> None:
        super().__init__(result["failure_code"])
        self.result = result


def verified_inputs(manifest: Any, supplied: Mapping[str, bytes], *, manifest_schema: str, benchmark_id: str,
                    required: Sequence[str], result_schema: str, retry: str) -> dict[str, Any]:
    """Return {name: parsed JSON} for every required input whose bytes match the manifest."""
    def fail(code: str, predicate: str, repair: str, **evidence: Any) -> Refused:
        return Refused(six(benchmark_id, result_schema, retry, "FAIL_CLOSED", code, predicate, repair,
                           "after the named input is supplied or corrected", **evidence))

    if not isinstance(manifest, Mapping) or manifest.get("schema") != manifest_schema:
        raise fail("INPUT_MANIFEST_SCHEMA", f"manifest schema == {manifest_schema}", "supply an input manifest")
    if manifest.get("benchmark_id") != benchmark_id:
        raise fail("INPUT_MANIFEST_BENCHMARK", f"manifest benchmark_id == {benchmark_id}", f"bind the manifest to {benchmark_id}")
    declared = manifest.get("inputs") if isinstance(manifest.get("inputs"), Mapping) else {}
    parsed: dict[str, Any] = {}
    for name in required:
        entry = declared.get(name)
        if not isinstance(entry, Mapping):
            raise fail("INPUT_NOT_SUPPLIED", f"manifest declares input {name}",
                       f"declare {name} as owner/repo:path@revision with its sha256", input=name)
        ref, digest = entry.get("ref"), entry.get("sha256")
        if not (isinstance(ref, str) and _REF.match(ref) and isinstance(digest, str) and _SHA.match(digest)):
            raise fail("INPUT_REFERENCE_MALFORMED", f"{name} is owner/repo:path@<40-hex revision> with a 64-hex sha256",
                       f"pin {name} to an exact revision and digest", input=name)
        if name not in supplied:
            raise fail("INPUT_NOT_SUPPLIED", f"caller supplies the bytes of {name} ({ref})",
                       f"pass --input {name}=<path to the bytes of {ref}>", input=name, ref=ref)
        actual = hashlib.sha256(supplied[name]).hexdigest()
        if actual != digest:
            raise fail("INPUT_DIGEST_MISMATCH", f"sha256({name}) == declared {digest}", f"supply the exact bytes of {ref}",
                       input=name, actual_sha256=actual)
        try:
            parsed[name] = json.loads(supplied[name].decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise fail("INPUT_NOT_JSON", f"{name} is UTF-8 JSON", f"supply {name} as JSON", input=name) from None
    return parsed


def canonical_sha256(value: Any) -> str:
    """Digest of the canonical JSON form (sorted keys, no whitespace, UTF-8)."""
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def read_cli_inputs(pairs: Sequence[str]) -> dict[str, bytes]:
    from pathlib import Path

    supplied: dict[str, bytes] = {}
    for item in pairs:
        name, sep, path = item.partition("=")
        if not sep:
            raise ValueError(f"--input must be NAME=PATH: {item}")
        supplied[name] = Path(path).read_bytes()
    return supplied
