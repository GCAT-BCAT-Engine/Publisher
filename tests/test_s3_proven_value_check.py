"""S3_PROVEN_VALUE evaluator. Every order and policy here is SYNTHETIC and NON-AUTHORITATIVE."""
import copy
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
import s3_proven_value_check as s3  # noqa: E402

REV = "0" * 40


def order(i, arm, value, **overrides):
    row = {"order_id": f"SYNTHETIC-{i}", "arm": arm, "value": value,
           "receipt_ref": f"org-ledger://SYNTHETIC/receipt/{i}", "receipt_sha256": hashlib.sha256(str(i).encode()).hexdigest()}
    row.update(overrides)
    return row


def outcomes(rows=None, **overrides):
    value = {"schema": s3.OUTCOMES_SCHEMA, "metric": "net_saving_usd", "synthetic": True,
             "orders": rows if rows is not None else [order(1, "HUMAN_SERVICE", "12.00"), order(2, "HUMAN_SERVICE", "10.50"),
                                                      order(3, "BASELINE", "8.00"), order(4, "BASELINE", "8.75")]}
    value.update(overrides)
    return value


def policy(**overrides):
    value = {"schema": s3.POLICY_SCHEMA, "metric": "net_saving_usd", "min_orders_per_arm": 2, "min_effect": "2.5"}
    value.update(overrides)
    return value


def bundle(o=None, p=None, drop=(), fixture=True):
    docs = {"service_outcomes": o or outcomes(), "study_policy": p or policy()}
    data = {k: json.dumps(v, sort_keys=True).encode() for k, v in docs.items()}
    manifest = {"schema": s3.MANIFEST_SCHEMA, "benchmark_id": "S3_PROVEN_VALUE", "fixture": fixture, "inputs": {
        k: {"ref": f"StegVerse-Labs/Marketplace:synthetic/{k}.json@{REV}", "sha256": hashlib.sha256(v).hexdigest()}
        for k, v in data.items()}}
    return manifest, {k: v for k, v in data.items() if k not in drop}


class S3ProvenValueTests(unittest.TestCase):
    def test_allow_with_exact_difference(self):
        out = s3.evaluate(*bundle())
        value = out["predicates"]["VALUE_ADDED"]
        # (12.00 + 10.50)/2 = 11.25; (8.00 + 8.75)/2 = 8.375; difference 2.875 >= 2.5
        self.assertEqual((value["mean_human_service"], value["mean_baseline"], value["difference"]), ("11.25", "8.375", "2.875"))
        self.assertEqual((out["disposition"], out["evidence_class"]), ("ALLOW", "FIXTURE_NOT_EVIDENCE"))
        self.assertIs(out["authority"]["benchmark_completion_granted"], False)

    def test_non_string_identity_values_fail_closed_not_crash(self):
        # Lane B review defect 1: a list or object as order_id/receipt raised TypeError (unhashable), no six fields.
        for key in ("order_id", "receipt_ref", "receipt_sha256"):
            for bad in (["x"], {"a": 1}, 7):
                with self.subTest(key=key, value=bad):
                    rows = outcomes()["orders"]
                    rows[0] = order(1, "HUMAN_SERVICE", "12.00", **{key: bad})
                    with self.assertRaises(ref.Refused) as raised:
                        s3.evaluate(*bundle(outcomes(rows)))
                    result = raised.exception.result
                    self.assertEqual((result["disposition"], result["failure_code"]), ("FAIL_CLOSED", "INPUT_VALUE_INVALID"))
        rows = outcomes()["orders"]
        rows[0] = order(1, ["HUMAN_SERVICE"], "12.00")
        with self.assertRaises(ref.Refused):
            s3.evaluate(*bundle(outcomes(rows)))

    def test_each_predicate_denies_by_name(self):
        rows = outcomes()["orders"]
        cases = {
            "VALUE_ADDED": bundle(p=policy(min_effect="3")),
            "SAMPLE_SUFFICIENT": bundle(p=policy(min_orders_per_arm=3)),
            "ORDERS_ATTRIBUTABLE": bundle(o=outcomes([*rows[:3], order(4, "BASELINE", "8.75", receipt_ref="file:///x")])),
            "NO_FABRICATED_ORDERS": bundle(o=outcomes([*rows[:3], order(4, "BASELINE", "8.75", order_id="SYNTHETIC-1")])),
        }
        for predicate, args in cases.items():
            with self.subTest(predicate=predicate):
                out = s3.evaluate(*args)
                self.assertEqual(out["disposition"], "DENY")
                self.assertIn(predicate, out["evidence"]["failed_predicates"])

    def test_synthetic_outcomes_are_fabricated_outside_a_fixture(self):
        out = s3.evaluate(*bundle(fixture=False))
        self.assertEqual(out["failed_predicate"], "NO_FABRICATED_ORDERS")
        real = s3.evaluate(*bundle(o=outcomes(synthetic=False), fixture=False))
        self.assertEqual((real["disposition"], real["evidence_class"]), ("ALLOW", "SOURCE_IMPLEMENTED"))

    def test_reused_receipt_is_fabrication(self):
        rows = outcomes()["orders"]
        dup = order(4, "BASELINE", "8.75", receipt_sha256=rows[0]["receipt_sha256"])
        out = s3.evaluate(*bundle(o=outcomes([*rows[:3], dup])))
        self.assertIn("NO_FABRICATED_ORDERS", out["evidence"]["failed_predicates"])

    def test_missing_outcomes_is_input_not_supplied_by_name(self):
        for name in s3.REQUIRED_INPUTS:
            with self.subTest(name=name):
                with self.assertRaises(ref.Refused) as raised:
                    s3.evaluate(*bundle(drop=(name,)))
                self.assertEqual((raised.exception.result["failure_code"], raised.exception.result["evidence"]["input"]),
                                 ("INPUT_NOT_SUPPLIED", name))

    def test_invalid_values_fail_closed(self):
        for args in (bundle(o=outcomes([order(1, "HUMAN_SERVICE", 12.0)])), bundle(o=outcomes([order(1, "OTHER", "1")])),
                     bundle(p=policy(min_orders_per_arm=0)), bundle(p=policy(metric="other"))):
            with self.subTest():
                with self.assertRaises(ref.Refused) as raised:
                    s3.evaluate(*args)
                self.assertEqual(raised.exception.result["failure_code"], "INPUT_VALUE_INVALID")

    def test_deterministic_and_input_not_mutated(self):
        manifest, supplied = bundle()
        snapshot = copy.deepcopy((manifest, supplied))
        self.assertEqual(json.dumps(s3.evaluate(manifest, supplied), sort_keys=True),
                         json.dumps(s3.evaluate(manifest, supplied), sort_keys=True))
        self.assertEqual((manifest, supplied), snapshot)

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            d = Path(directory)
            for args, code in ((bundle(), 0), (bundle(p=policy(min_effect="9")), 2), (bundle(drop=("service_outcomes",)), 1)):
                manifest, supplied = args
                (d / "m.json").write_text(json.dumps(manifest), encoding="utf-8")
                cmd = [sys.executable, str(ROOT / "tools/s3_proven_value_check.py"), str(d / "m.json")]
                for name, data in supplied.items():
                    (d / f"{name}.json").write_bytes(data)
                    cmd += ["--input", f"{name}={d / f'{name}.json'}"]
                self.assertEqual(subprocess.run(cmd, capture_output=True, text=True).returncode, code)


if __name__ == "__main__":
    unittest.main()
