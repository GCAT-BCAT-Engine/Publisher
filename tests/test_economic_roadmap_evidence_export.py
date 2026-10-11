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


def readback(**overrides):
    record = {
        "schema": ex.READBACK_SCHEMA,
        "goal_task_id": ex.TASK_ID,
        "benchmark_id": "S1_CHATGPT",
        "predicate": "reconstruction_PASS",
        "disposition": "ALLOW",
        "synthetic": False,
        "master_records_state": "RECORDED",
        "reconstruction_status": "PASS",
        "required_evidence_validation_status": "PASS",
        "receipt_sha256": DIGEST,
        "reconstructed_receipt_sha256": DIGEST,
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

    def test_each_closure_failure_refused_with_exact_predicate(self):
        cases = {
            "readback_schema": {"schema": "other"},
            "goal_task_identity": {"goal_task_id": "OTHER-TASK"},
            "correct_benchmark_identity": {"benchmark_id": "S9_UNKNOWN"},
            "predicate_identity": {"predicate": "has space"},
            "public_safe_evidence_ref": {"evidence_ref": "mykv://device/private-state"},
            "governed_disposition_required": {"disposition": None},
            "evidence_not_declared_non_synthetic": {"synthetic": True},
            "master_records_state_RECORDED": {"master_records_state": "PENDING"},
            "reconstruction_PASS": {"reconstruction_status": "FAIL"},
            "required_evidence_validation_PASS": {"required_evidence_validation_status": "UNKNOWN"},
            "exact_receipt_digest_equality": {"reconstructed_receipt_sha256": "d" * 64},
            "organization_receipt_ref": {"organization_receipt_ref": None},
        }
        for expected, overrides in cases.items():
            with self.subTest(expected=expected):
                out = ex.export([readback(**overrides)])
                self.assertEqual(out["benchmarks"], {})
                self.assertEqual(out["refused"][0]["failed_predicate"], expected)
                self.assertEqual(out["refused"][0]["disposition"], "FAIL_CLOSED")

    def test_missing_digests_are_not_equal(self):
        out = ex.export([readback(receipt_sha256=None, reconstructed_receipt_sha256=None)])
        self.assertEqual(out["refused"][0]["failed_predicate"], "exact_receipt_digest_equality")

    def test_ci_merge_and_issue_signals_cannot_substitute(self):
        record = readback(disposition="ALLOW", master_records_state=None)
        record.update({"ci_checks": "SUCCESS", "pr_merged": True, "issue_closed": True})
        out = ex.export([record])
        self.assertEqual(out["benchmarks"], {})
        self.assertEqual(out["refused"][0]["failed_predicate"], "master_records_state_RECORDED")

    def test_non_allow_disposition_exported_as_failure(self):
        out = ex.export([readback(disposition="DENY", failed_predicate="exact_external_intr_ingress_allow",
                                  master_records_state=None)])
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
        self.assertEqual(out["refused"][0]["failed_predicate"], "malformed_readback_record")

    def test_input_not_mutated(self):
        record = readback()
        snapshot = copy.deepcopy(record)
        ex.export([record])
        self.assertEqual(record, snapshot)

    def test_cli_default_is_empty_projection(self):
        result = subprocess.run([sys.executable, "-m", "publisher.economic_roadmap_evidence_export"],
                                cwd=ROOT, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout), ex.export([]))


if __name__ == "__main__":
    unittest.main()
