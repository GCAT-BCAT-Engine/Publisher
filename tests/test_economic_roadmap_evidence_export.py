import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

from publisher import economic_roadmap_evidence_export as ex

ROOT = Path(__file__).resolve().parents[1]
COMMITTED = ROOT / "data/economy/economic-roadmap-evidence.v1.json"
DIGEST = "c" * 64


CLOSURE_KEYS = {"state", "master_record_ref", "receipt_sha256", "reconstructed_receipt_sha256",
                "reconstruction_status", "required_evidence_validation_status"}


def closure(**overrides):
    """Shape returned by LLM-adapter record_governed_publication_closure on success."""
    value = {
        "schema": "stegverse.external-framework-wiki-publication-governed-closure/v1",
        "state": "RECORDED",
        "master_record_ref": "master-records://record/" + DIGEST,
        "custody_receipt_id": "custody-1",
        "receipt_sha256": DIGEST,
        "reconstructed_receipt_sha256": DIGEST,
        "reconstruction_status": "PASS",
        "required_evidence_validation_status": "PASS",
        "gates_publication": False,
        "master_records_grants_transition_authority": False,
        "authority_effect": "NONE_DOWNSTREAM_RECORDING_ONLY",
    }
    value.update(overrides)
    return value


def readback(closure_overrides=None, **overrides):
    record = {
        "schema": ex.INPUT_SCHEMA,
        "goal_task_id": ex.TASK_ID,
        "benchmark_id": "S1_CHATGPT",
        "predicate": "reconstruction_PASS",
        "disposition": "ALLOW",
        "synthetic": False,
        "master_records_closure": closure(**(closure_overrides or {})),
        "evidence_ref": "master-records://organization/StegVerse-Labs/receipt/" + DIGEST,
        "organization_receipt_ref": "org-ledger://StegVerse-Labs/receipt/" + DIGEST,
        "private_note": "operator-only context",
    }
    record.update(overrides)
    return record


class EconomicRoadmapEvidenceExportTests(unittest.TestCase):
    def test_empty_export_grants_nothing(self):
        out = ex.export([])
        self.assertEqual(out["schema"], "stegverse.economic-roadmap-evidence/v1")
        self.assertEqual(out["source"], "PUBLISHER_GOVERNED_PROJECTION")
        self.assertEqual(out["benchmarks"], {})
        self.assertEqual(out["authority_effect"], "NONE")
        self.assertIs(out["publication_executed"], False)
        self.assertIs(out["benchmark_completion_granted"], False)
        self.assertIs(out["readback_authenticated_by_this_module"], False)

    def test_committed_projection_matches_empty_export(self):
        self.assertEqual(json.loads(COMMITTED.read_text(encoding="utf-8")), ex.export([]))

    def test_valid_readback_exported_public_safe(self):
        out = ex.export([readback()])
        entry = out["benchmarks"]["S1_CHATGPT"]["reconstruction_PASS"]
        self.assertEqual(entry["evidence_class"], "MASTER_RECORDS_VERIFIED")
        self.assertEqual(entry["receipt_sha256"], entry["reconstructed_receipt_sha256"])
        self.assertNotIn("private_note", entry)
        self.assertEqual(out["refused"], [])

    def test_public_reference_never_exports_embedded_credentials_or_controls(self):
        for ref in ("https://user:password@example.org/receipt",
                    "https://example.org/receipt\\x00private",
                    "https://example.org/receipt\\x1fprivate"):
            with self.subTest(ref=repr(ref)):
                result = ex.export([readback(evidence_ref=ref)])
                self.assertEqual(result["benchmarks"], {})
                self.assertEqual(result["refused"][0]["failed_predicate"], "public_safe_evidence_ref")

    def test_each_closure_failure_refused_with_exact_predicate(self):
        cases = {
            "input_schema": {"schema": "stegverse.master-records.benchmark-reconstruction-readback/v1"},
            "goal_task_identity": {"goal_task_id": "OTHER-TASK"},
            "correct_benchmark_identity": {"benchmark_id": "S9_UNKNOWN"},
            "predicate_identity": {"predicate": "has space"},
            "public_safe_evidence_ref": {"evidence_ref": "mykv://device/private-state"},
            "governed_disposition_required": {"disposition": None},
            "evidence_not_declared_non_synthetic": {"synthetic": True},
            "master_records_closure_required": {"master_records_closure": None},
            "organization_receipt_ref": {"organization_receipt_ref": None},
        }
        for expected, overrides in cases.items():
            with self.subTest(expected=expected):
                out = ex.export([readback(**overrides)])
                self.assertEqual(out["benchmarks"], {})
                self.assertEqual(out["refused"][0]["failed_predicate"], expected)
                self.assertEqual(out["refused"][0]["disposition"], "FAIL_CLOSED")

    def test_each_master_records_closure_failure_refused_with_exact_predicate(self):
        cases = {
            "master_records_state_RECORDED": {"state": "NOT_RECORDED"},
            "reconstruction_PASS": {"reconstruction_status": "FAIL"},
            "required_evidence_validation_PASS": {"required_evidence_validation_status": "UNKNOWN"},
            "exact_receipt_digest_equality": {"reconstructed_receipt_sha256": "d" * 64},
            "master_record_ref": {"master_record_ref": ""},
            "master_records_closure_schema": {"schema": "stegverse.governed-publication-master-records-closure/v1"},
            "master_records_closure_authority_boundary": {"master_records_grants_transition_authority": True},
        }
        for expected, overrides in cases.items():
            with self.subTest(expected=expected):
                out = ex.export([readback(overrides)])
                self.assertEqual(out["benchmarks"], {})
                self.assertEqual(out["refused"][0]["failed_predicate"], expected)

    def test_not_recorded_closure_from_existing_path_is_refused(self):
        not_recorded = {"schema": ex.CLOSURE_SCHEMA,
                        "state": "NOT_RECORDED", "disposition": "NOT_RECORDED",
                        "failure_code": "master_records_recorder_not_configured", "receipt_sha256": DIGEST,
                        "gates_publication": False, "master_records_grants_transition_authority": False,
                        "authority_effect": "NONE"}
        out = ex.export([readback(master_records_closure=not_recorded)])
        self.assertEqual(out["benchmarks"], {})
        self.assertEqual(out["refused"][0]["failed_predicate"], "master_records_state_RECORDED")

    def test_flat_master_records_fields_without_closure_are_refused(self):
        record = readback()
        flat = record.pop("master_records_closure")
        record.update({k: flat[k] for k in CLOSURE_KEYS})
        out = ex.export([record])
        self.assertEqual(out["refused"][0]["failed_predicate"], "master_records_closure_required")

    def test_master_record_reference_must_be_public_safe(self):
        for ref in ("mykv://private/record", "skap://vault/receipt", "tvc://lease/secret",
                    "secret://token", "wallet://key", "not-a-uri", "https://invalid ref", ""):
            with self.subTest(ref=ref):
                out = ex.export([readback({"master_record_ref": ref})])
                self.assertEqual(out["benchmarks"], {})
                self.assertEqual(out["refused"][0]["failed_predicate"], "master_record_ref")
        self.assertEqual(ex.export([readback()])["refused"], [])

    def test_organization_receipt_ref_must_be_independent_of_evidence_ref(self):
        row = readback()
        row["organization_receipt_ref"] = row["evidence_ref"]
        out = ex.export([row])
        self.assertEqual(out["benchmarks"], {})
        self.assertEqual(out["refused"][0]["failed_predicate"], "independent_organization_receipt_ref")
        self.assertEqual(ex.export([readback()])["refused"], [])

    def test_master_record_ref_must_be_independent_of_benchmark_evidence(self):
        row = readback()
        row["master_records_closure"]["master_record_ref"] = row["evidence_ref"]
        result = ex.export([row])
        self.assertEqual(result["benchmarks"], {})
        self.assertEqual(result["refused"][0]["failed_predicate"], "independent_master_record_ref")
        self.assertEqual(ex.export([readback()])["refused"], [])

    def test_organization_and_master_record_refs_must_be_independent(self):
        row = readback(closure_overrides={"master_record_ref": "org-ledger://StegVerse-Labs/receipt/" + DIGEST})
        result = ex.export([row])
        self.assertEqual(result["benchmarks"], {})
        self.assertEqual(result["refused"][0]["failed_predicate"], "independent_organization_master_record_refs")

    def test_missing_digests_are_not_equal(self):
        out = ex.export([readback({"receipt_sha256": None, "reconstructed_receipt_sha256": None})])
        self.assertEqual(out["refused"][0]["failed_predicate"], "exact_receipt_digest_equality")

    def test_ci_merge_and_issue_signals_cannot_substitute(self):
        record = readback({"state": None})
        record.update({"ci_checks": "SUCCESS", "pr_merged": True, "issue_closed": True})
        out = ex.export([record])
        self.assertEqual(out["benchmarks"], {})
        self.assertEqual(out["refused"][0]["failed_predicate"], "master_records_state_RECORDED")

    def test_non_allow_disposition_exported_as_failure(self):
        out = ex.export([readback({"state": None}, disposition="DENY",
                                  failed_predicate="exact_external_intr_ingress_allow")])
        entry = out["benchmarks"]["S1_CHATGPT"]["reconstruction_PASS"]
        self.assertEqual(entry, {"disposition": "DENY", "failed_predicate": "exact_external_intr_ingress_allow",
                                 "evidence_ref": readback()["evidence_ref"]})
        out = ex.export([readback(disposition="FAIL_CLOSED")])
        self.assertEqual(out["refused"][0]["failed_predicate"], "non_allow_failed_predicate_required")

    def test_duplicate_predicate_evidence_refused_entirely(self):
        out = ex.export([readback(), readback(), readback()])
        self.assertEqual(out["benchmarks"], {})
        self.assertEqual(len(out["refused"]), 3)
        self.assertTrue(all(r["failed_predicate"] == "duplicate_predicate_evidence" for r in out["refused"]))

    def test_rejects_non_list_input_and_malformed_rows(self):
        with self.assertRaises(ex.EconomicRoadmapEvidenceError):
            ex.export({"records": []})
        out = ex.export(["not-a-record"])
        self.assertEqual(out["refused"][0]["failed_predicate"], "malformed_closure_record")

    def test_input_not_mutated(self):
        record = readback()
        snapshot = copy.deepcopy(record)
        ex.export([record])
        self.assertEqual(record, snapshot)

    def test_cli_default_is_empty_projection(self):
        result = subprocess.run([sys.executable, "-m", "publisher.economic_roadmap_evidence_export"],
                                cwd=ROOT, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout), ex.export([]))


    def test_closure_claiming_authority_beyond_recording_is_refused(self):
        for overrides in ({"authority_effect": "ALLOW"}, {"gates_publication": True},
                          {"master_records_grants_transition_authority": None}):
            with self.subTest(overrides=overrides):
                out = ex.export([readback(overrides)])
                self.assertEqual(out["benchmarks"], {})
                self.assertEqual(out["refused"][0]["failed_predicate"], "master_records_closure_authority_boundary")

if __name__ == "__main__":
    unittest.main()
