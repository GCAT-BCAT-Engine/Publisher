"""S2_PRIVACY evaluator. Every result, policy and authorization here is SYNTHETIC and NON-AUTHORITATIVE."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import benchmark_input_reference as ref  # noqa: E402
import s2_privacy_disclosure_check as s2p  # noqa: E402

REV = "0" * 40
PURPOSE = "monthly category totals for the subject cohort (SYNTHETIC)"


def result(cells=None, **overrides):
    value = {"schema": s2p.RESULT_IN_SCHEMA, "purpose": PURPOSE,
             "cells": cells if cells is not None else [{"fields": {"category": "food", "monthly_total": "1200"}, "subject_count": 12},
                                                       {"fields": {"category": "travel", "monthly_total": "800"}, "subject_count": 10}]}
    value.update(overrides)
    return value


def policy(**overrides):
    value = {"schema": s2p.POLICY_SCHEMA, "purpose": PURPOSE, "allowed_fields": ["category", "monthly_total"],
             "raw_state_fields": ["account_number", "transaction_id", "balance"], "min_subjects_per_cell": 10}
    value.update(overrides)
    return value


def auth(r=None, **overrides):
    value = {"schema": s2p.AUTH_SCHEMA, "purpose": PURPOSE, "result_sha256": ref.canonical_sha256(r or result())}
    value.update(overrides)
    return value


def bundle(r=None, p=None, a=None, extra=None):
    r = r or result()
    docs = {"disclosed_result": r, "disclosure_policy": p or policy(), "authorization_record": a or auth(r)}
    docs.update(extra or {})
    data = {k: json.dumps(v, sort_keys=True).encode() for k, v in docs.items()}
    manifest = {"schema": s2p.MANIFEST_SCHEMA, "benchmark_id": "S2_PRIVACY", "fixture": True, "inputs": {
        k: {"ref": f"StegVerse-Labs/SKAP:synthetic/{k}.json@{REV}", "sha256": hashlib.sha256(v).hexdigest()} for k, v in data.items()}}
    return manifest, data


class S2PrivacyTests(unittest.TestCase):
    def test_buildable_predicates_hold_and_owner_gate_names_skap_receipt(self):
        out = s2p.evaluate(*bundle())
        self.assertTrue(all(out["predicates"][p]["holds"] for p in s2p.BUILDABLE))
        self.assertEqual((out["disposition"], out["failure_code"], out["failed_predicate"], out["evidence"]["input"]),
                         ("FAIL_CLOSED", "INPUT_NOT_SUPPLIED", "AUTHORIZED_RESULT_AUTHENTIC", "skap_execution_receipt"))
        self.assertIs(out["authority"]["benchmark_completion_granted"], False)

    def test_with_skap_receipt_the_next_gate_is_the_independent_validator_policy(self):
        out = s2p.evaluate(*bundle(extra={"skap_execution_receipt": {"synthetic": True}}))
        self.assertEqual((out["failure_code"], out["evidence"]["input"]), ("INPUT_NOT_SUPPLIED", "independent_validator_policy"))

    def test_allow_is_unreachable_without_owner_verifiers(self):
        out = s2p.evaluate(*bundle(extra={"skap_execution_receipt": {"synthetic": True},
                                          "independent_validator_policy": {"synthetic": True}}))
        self.assertEqual((out["disposition"], out["failure_code"]), ("FAIL_CLOSED", "OWNER_VERIFIER_UNDEFINED"))

    def test_each_buildable_predicate_denies_by_name(self):
        leak = result([{"fields": {"category": "food", "account_number": "x"}, "subject_count": 12}])
        outside = result([{"fields": {"category": "food", "merchant": "x"}, "subject_count": 12}])
        small = result([{"fields": {"category": "food", "monthly_total": "5"}, "subject_count": 9}])
        cases = {
            "RESULT_FIELDS_WITHIN_DECLARED_PURPOSE": bundle(r=outside),
            "NO_RAW_STATE_FIELDS": bundle(r=leak),
            "AGGREGATION_THRESHOLD": bundle(r=small),
            "RESULT_DIGEST_BOUND_TO_AUTHORIZATION": bundle(a=auth(result_sha256="f" * 64)),
        }
        for predicate, args in cases.items():
            with self.subTest(predicate=predicate):
                out = s2p.evaluate(*args)
                self.assertEqual(out["disposition"], "DENY")
                self.assertIn(predicate, out["evidence"]["failed_predicates"])

    def test_purpose_mismatch_is_outside_declared_purpose(self):
        out = s2p.evaluate(*bundle(a=auth(purpose="something else")))
        self.assertIn("RESULT_FIELDS_WITHIN_DECLARED_PURPOSE", out["evidence"]["failed_predicates"])

    def test_missing_required_input_is_input_not_supplied_by_name(self):
        for name in s2p.REQUIRED_INPUTS:
            with self.subTest(name=name):
                manifest, data = bundle()
                data.pop(name)
                with self.assertRaises(ref.Refused) as raised:
                    s2p.evaluate(manifest, data)
                self.assertEqual(raised.exception.result["evidence"]["input"], name)

    def test_invalid_shapes_fail_closed(self):
        for args in (bundle(p=policy(min_subjects_per_cell=0)), bundle(r=result([{"fields": {}, "subject_count": "12"}]))):
            with self.subTest():
                with self.assertRaises(ref.Refused) as raised:
                    s2p.evaluate(*args)
                self.assertEqual(raised.exception.result["failure_code"], "INPUT_VALUE_INVALID")

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            d = Path(directory)
            for args, code in ((bundle(), 1), (bundle(a=auth(result_sha256="f" * 64)), 2)):
                manifest, data = args
                (d / "m.json").write_text(json.dumps(manifest), encoding="utf-8")
                cmd = [sys.executable, str(ROOT / "tools/s2_privacy_disclosure_check.py"), str(d / "m.json")]
                for name, raw in data.items():
                    (d / f"{name}.json").write_bytes(raw)
                    cmd += ["--input", f"{name}={d / f'{name}.json'}"]
                self.assertEqual(subprocess.run(cmd, capture_output=True, text=True).returncode, code)


if __name__ == "__main__":
    unittest.main()
