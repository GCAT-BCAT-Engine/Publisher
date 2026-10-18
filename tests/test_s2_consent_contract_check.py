"""S2_CONSENT evaluator. Every contract and record here is SYNTHETIC and NON-AUTHORITATIVE."""
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
import s2_consent_contract_check as s2  # noqa: E402

REV = "0" * 40


def contract(**overrides):
    value = {
        "schema": s2.CONTRACT_SCHEMA, "purpose": "aggregate spending insight for the subject (SYNTHETIC)",
        "terms": "SYNTHETIC NON-AUTHORITATIVE terms", "scope": ["spending_categories", "monthly_totals"],
        "duration": {"start": "2026-11-01", "end": "2027-10-31"},
        "derivative_rights": [{"right": "aggregate_statistics", "within_scope": "monthly_totals"}],
        "fee": {"amount": "4.50", "currency": "USD", "basis": "per_month"},
        "revocation": {"available_to_subject": True, "prospective_only": True, "notice_period_days": 0,
                       "procedure_ref": "skap://SYNTHETIC/revoke"},
    }
    value.update(overrides)
    return value


def record(c=None, **overrides):
    value = {"schema": s2.RECORD_SCHEMA, "contract_sha256": ref.canonical_sha256(c or contract()),
             "subject_ref": "pseudonym:SYNTHETIC-1", "accepted_at": "2026-11-02"}
    value.update(overrides)
    return value


def bundle(c=None, r=None, drop=(), fixture=True):
    c = c or contract()
    docs = {"consent_contract": c, "consent_record": r if r is not None else record(c)}
    supplied = {k: json.dumps(v, sort_keys=True).encode() for k, v in docs.items() if k not in drop}
    data = {k: json.dumps(v, sort_keys=True).encode() for k, v in docs.items()}
    manifest = {"schema": s2.MANIFEST_SCHEMA, "benchmark_id": "S2_CONSENT", "fixture": fixture, "inputs": {
        k: {"ref": f"StegVerse-Labs/MyKV:synthetic/{k}.json@{REV}", "sha256": hashlib.sha256(v).hexdigest()}
        for k, v in data.items()}}
    return manifest, supplied


class S2ConsentTests(unittest.TestCase):
    def test_allow_and_fixture_is_never_evidence(self):
        out = s2.evaluate(*bundle())
        self.assertEqual(out["disposition"], "ALLOW")
        self.assertEqual(out["evidence_class"], "FIXTURE_NOT_EVIDENCE")
        self.assertIs(out["authority"]["benchmark_completion_granted"], False)
        self.assertEqual(s2.evaluate(*bundle(fixture=False))["evidence_class"], "SOURCE_IMPLEMENTED")

    def test_each_predicate_denies_by_name(self):
        c = contract()
        cases = {
            "TERMS_COMPLETE": contract(purpose=""),
            "DURATION_BOUNDED": contract(duration={"start": "2027-10-31", "end": "2026-11-01"}),
            "FEE_EXACT": contract(fee={"amount": "-1", "currency": "USD", "basis": "per_month"}),
            "REVOCATION_PROSPECTIVE": contract(revocation={**c["revocation"], "prospective_only": False}),
            "DERIVATIVE_RIGHTS_BOUNDED": contract(derivative_rights=[{"right": "UNLIMITED", "within_scope": "monthly_totals"}]),
        }
        for predicate, doc in cases.items():
            with self.subTest(predicate=predicate):
                out = s2.evaluate(*bundle(c=doc, r=record(doc)))
                self.assertEqual(out["disposition"], "DENY")
                self.assertIn(predicate, out["evidence"]["failed_predicates"])
                for field in ("failure_code", "failed_predicate", "required_evidence_or_repair", "retry_entrypoint",
                              "owning_existing_goal", "next_attempt"):
                    self.assertTrue(out[field])

    def test_reconstruction_requires_matching_digest_and_acceptance_in_window(self):
        for r in (record(contract_sha256="f" * 64), record(accepted_at="2028-01-01"), record(subject_ref="")):
            with self.subTest(r=r):
                out = s2.evaluate(*bundle(r=r))
                self.assertEqual((out["disposition"], out["failed_predicate"]), ("DENY", "INDEPENDENTLY_RECONSTRUCTABLE"))

    def test_changed_contract_terms_break_reconstruction(self):
        original = contract()
        changed = contract(fee={"amount": "9.00", "currency": "USD", "basis": "per_month"})
        out = s2.evaluate(*bundle(c=changed, r=record(original)))
        self.assertEqual(out["failed_predicate"], "INDEPENDENTLY_RECONSTRUCTABLE")

    def test_missing_owner_record_is_input_not_supplied_by_name(self):
        for name in s2.REQUIRED_INPUTS:
            with self.subTest(name=name):
                with self.assertRaises(ref.Refused) as raised:
                    s2.evaluate(*bundle(drop=(name,)))
                self.assertEqual((raised.exception.result["failure_code"], raised.exception.result["evidence"]["input"]),
                                 ("INPUT_NOT_SUPPLIED", name))

    def test_digest_and_reference_verified(self):
        manifest, supplied = bundle()
        supplied["consent_record"] += b" "
        with self.assertRaises(ref.Refused) as raised:
            s2.evaluate(manifest, supplied)
        self.assertEqual(raised.exception.result["failure_code"], "INPUT_DIGEST_MISMATCH")
        manifest, supplied = bundle()
        manifest["inputs"]["consent_contract"]["ref"] = "https://example.org/c.json"
        with self.assertRaises(ref.Refused) as raised:
            s2.evaluate(manifest, supplied)
        self.assertEqual(raised.exception.result["failure_code"], "INPUT_REFERENCE_MALFORMED")

    def test_deterministic_and_input_not_mutated(self):
        manifest, supplied = bundle()
        snapshot = copy.deepcopy((manifest, supplied))
        self.assertEqual(json.dumps(s2.evaluate(manifest, supplied), sort_keys=True),
                         json.dumps(s2.evaluate(manifest, supplied), sort_keys=True))
        self.assertEqual((manifest, supplied), snapshot)

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            d = Path(directory)
            for kwargs, code in (({}, 0), ({"c": contract(purpose=""), "r": record(contract(purpose=""))}, 2),
                                 ({"drop": ("consent_record",)}, 1)):
                manifest, supplied = bundle(**kwargs)
                (d / "m.json").write_text(json.dumps(manifest), encoding="utf-8")
                args = [sys.executable, str(ROOT / "tools/s2_consent_contract_check.py"), str(d / "m.json")]
                for name, data in supplied.items():
                    (d / f"{name}.json").write_bytes(data)
                    args += ["--input", f"{name}={d / f'{name}.json'}"]
                self.assertEqual(subprocess.run(args, capture_output=True, text=True).returncode, code)


if __name__ == "__main__":
    unittest.main()
