#!/usr/bin/env python3
"""Roadmap benchmark S2_CONSENT: consent and compensation contract reconstructability.

S2_CONSENT (StegVerse-Labs/Site:data/economy/public-release-benchmarks.v1.json) requires
"purpose, terms, scope, duration, derivative rights, fee and future revocation
independently reconstructable". Two inputs, supplied by reference
(tools/benchmark_input_reference.py):

* ``consent_contract`` (``stegverse.mykv-consent-contract.v1``): the contract terms;
* ``consent_record`` (``stegverse.mykv-consent-record.v1``): the owner-side record of the
  accepted contract, carrying ``contract_sha256``, a pseudonymous ``subject_ref`` and
  ``accepted_at``. This is the SKAP/MyKV owner input; without it the answer is FAIL_CLOSED
  ``INPUT_NOT_SUPPLIED`` naming ``consent_record``.

Predicates:

* ``TERMS_COMPLETE``: all seven elements are present and non-empty;
* ``DURATION_BOUNDED``: ``duration.start`` < ``duration.end`` (UTC dates), never open-ended;
* ``FEE_EXACT``: the fee is an exact non-negative decimal with a currency and a basis;
* ``REVOCATION_PROSPECTIVE``: revocation is available to the subject, prospective only,
  with a notice period of at least zero days and a named procedure;
* ``DERIVATIVE_RIGHTS_BOUNDED``: derivative rights are listed explicitly, none is
  ``UNLIMITED`` and each is within the declared scope;
* ``INDEPENDENTLY_RECONSTRUCTABLE``: the canonical digest of the supplied contract equals
  the record's ``contract_sha256``, and the record was accepted inside the duration.

ALLOW, DENY (named predicate) or FAIL_CLOSED, each non-ALLOW with the six fields. A file
pair marked ``fixture`` yields fixture output that is never evidence. Nothing here grants
consent, completion or authority: completion stays a Publisher-governed closure.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping

sys.path.insert(0, str(Path(__file__).resolve().parent))
import benchmark_input_reference as ref  # noqa: E402

BENCHMARK_ID = "S2_CONSENT"
MANIFEST_SCHEMA = "stegverse.s2-consent-benchmark-inputs.v1"
CONTRACT_SCHEMA = "stegverse.mykv-consent-contract.v1"
RECORD_SCHEMA = "stegverse.mykv-consent-record.v1"
RESULT_SCHEMA = "stegverse.s2-consent-benchmark-result.v1"
RETRY = "python3 tools/s2_consent_contract_check.py <manifest.json> --input NAME=PATH ..."
REQUIRED_INPUTS = ("consent_contract", "consent_record")
ELEMENTS = ("purpose", "terms", "scope", "duration", "derivative_rights", "fee", "revocation")
PREDICATES = ("TERMS_COMPLETE", "DURATION_BOUNDED", "FEE_EXACT", "REVOCATION_PROSPECTIVE",
              "DERIVATIVE_RIGHTS_BOUNDED", "INDEPENDENTLY_RECONSTRUCTABLE")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _date(value: Any) -> date | None:
    if isinstance(value, str) and _DATE.match(value):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _nonempty(value: Any) -> bool:
    return (isinstance(value, str) and bool(value.strip())) or (isinstance(value, (list, dict)) and bool(value))


def _invalid(predicate: str, repair: str, **evidence: Any) -> ref.Refused:
    return ref.Refused(ref.six(BENCHMARK_ID, RESULT_SCHEMA, RETRY, "FAIL_CLOSED", "INPUT_VALUE_INVALID", predicate, repair,
                               "after the named input is corrected", **evidence))


def check(contract: Any, record: Any) -> dict[str, dict[str, Any]]:
    # A wrong document type is a malformed input, refused up front like S3 and S2_PRIVACY, not a DENY.
    if not isinstance(contract, Mapping) or contract.get("schema") != CONTRACT_SCHEMA:
        raise _invalid(f"consent_contract schema == {CONTRACT_SCHEMA}", "supply the consent contract", input="consent_contract")
    if not isinstance(record, Mapping) or record.get("schema") != RECORD_SCHEMA:
        raise _invalid(f"consent_record schema == {RECORD_SCHEMA}", "supply the consent record", input="consent_record")
    c, r = contract, record
    out: dict[str, dict[str, Any]] = {}
    missing = [e for e in ELEMENTS if not _nonempty(c.get(e))]
    out["TERMS_COMPLETE"] = {"holds": not missing, "missing": missing}

    duration = c.get("duration") if isinstance(c.get("duration"), Mapping) else {}
    start, end = _date(duration.get("start")), _date(duration.get("end"))
    out["DURATION_BOUNDED"] = {"holds": bool(start and end and start < end), "start": duration.get("start"),
                               "end": duration.get("end")}

    fee = c.get("fee") if isinstance(c.get("fee"), Mapping) else {}
    try:
        amount = Decimal(fee["amount"]) if isinstance(fee.get("amount"), str) else None
    except InvalidOperation:
        amount = None
    out["FEE_EXACT"] = {"holds": bool(amount is not None and amount.is_finite() and amount >= 0
                                      and _nonempty(fee.get("currency")) and _nonempty(fee.get("basis"))),
                        "amount": fee.get("amount"), "currency": fee.get("currency")}

    rev = c.get("revocation") if isinstance(c.get("revocation"), Mapping) else {}
    notice = rev.get("notice_period_days")
    out["REVOCATION_PROSPECTIVE"] = {"holds": bool(rev.get("available_to_subject") is True and rev.get("prospective_only") is True
                                                   and isinstance(notice, int) and not isinstance(notice, bool) and notice >= 0
                                                   and _nonempty(rev.get("procedure_ref")))}

    scope = c.get("scope") if isinstance(c.get("scope"), list) else []
    rights = c.get("derivative_rights") if isinstance(c.get("derivative_rights"), list) else []
    bad = [x for x in rights if not isinstance(x, Mapping) or x.get("right") == "UNLIMITED" or x.get("within_scope") not in scope]
    out["DERIVATIVE_RIGHTS_BOUNDED"] = {"holds": bool(rights) and not bad, "out_of_bounds": len(bad)}

    accepted = _date(r.get("accepted_at"))
    digest_ok = r.get("contract_sha256") == ref.canonical_sha256(contract)
    in_window = bool(accepted and start and end and start <= accepted <= end)
    out["INDEPENDENTLY_RECONSTRUCTABLE"] = {"holds": digest_ok and in_window and _nonempty(r.get("subject_ref")),
                                            "contract_sha256": ref.canonical_sha256(contract), "digest_matches": digest_ok,
                                            "accepted_within_duration": in_window}
    return out


def evaluate(manifest: Any, supplied: Mapping[str, bytes]) -> dict[str, Any]:
    inputs = ref.verified_inputs(manifest, supplied, manifest_schema=MANIFEST_SCHEMA, benchmark_id=BENCHMARK_ID,
                                 required=REQUIRED_INPUTS, result_schema=RESULT_SCHEMA, retry=RETRY)
    checks = check(inputs["consent_contract"], inputs["consent_record"])
    fixture = manifest.get("fixture") is True
    body = {"predicates": checks, "fixture": fixture,
            "evidence_class": "FIXTURE_NOT_EVIDENCE" if fixture else "SOURCE_IMPLEMENTED",
            "inputs": {name: dict(manifest["inputs"][name]) for name in REQUIRED_INPUTS}}
    failed = [p for p in PREDICATES if not checks[p]["holds"]]
    if failed:
        result = ref.six(BENCHMARK_ID, RESULT_SCHEMA, RETRY, "DENY", f"S2_CONSENT_{failed[0]}_NOT_MET", failed[0],
                         "supply a contract and record under which the named predicate holds",
                         "after the owner supplies a corrected contract or record", failed_predicates=failed)
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
    except (OSError, ValueError, TypeError) as exc:
        result = ref.six(BENCHMARK_ID, RESULT_SCHEMA, RETRY, "FAIL_CLOSED", "INPUT_MANIFEST_SCHEMA",
                         "manifest and inputs are readable", "supply readable files", "after the files are readable",
                         detail=f"{type(exc).__name__}: {exc}")
    print(json.dumps(result, indent=2, sort_keys=True))
    return {"ALLOW": 0, "DENY": 2}.get(result["disposition"], 1)


if __name__ == "__main__":
    raise SystemExit(main())
