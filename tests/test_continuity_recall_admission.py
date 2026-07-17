import json
import unittest
from pathlib import Path

from publisher.continuity_recall_admission import validate_export

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "continuity-recall"


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class ContinuityRecallAdmissionTests(unittest.TestCase):
    def test_valid_export_is_admitted_with_receipt(self):
        receipt = validate_export(load("admitted.json"))
        self.assertEqual(receipt["result"], "ADMITTED")
        self.assertEqual(receipt["evidence_count"], 1)
        self.assertEqual(len(receipt["receipt_sha256"]), 64)

    def test_exact_claim_without_payload_is_rejected(self):
        receipt = validate_export(load("rejected-exact-without-payload.json"))
        self.assertEqual(receipt["result"], "REJECTED")
        self.assertIn("evidence[0]:exact_payload_unavailable", receipt["reasons"])

    def test_revoked_authority_is_rejected(self):
        bundle = load("admitted.json")
        bundle["authorization"]["revoked"] = True
        receipt = validate_export(bundle)
        self.assertIn("authorization_revoked", receipt["reasons"])

    def test_wrong_destination_is_rejected(self):
        bundle = load("admitted.json")
        bundle["authorization"]["destination"] = "Other/Repo"
        receipt = validate_export(bundle)
        self.assertIn("destination_mismatch", receipt["reasons"])

    def test_policy_and_records_paths_are_rejected(self):
        for path in ("_Policy/Data_Sharing_Policy.md", "03_Records/medical.md"):
            with self.subTest(path=path):
                bundle = load("admitted.json")
                bundle["evidence"][0]["path"] = path
                receipt = validate_export(bundle)
                self.assertIn("evidence[0]:prohibited_path", receipt["reasons"])

    def test_derived_index_cannot_be_canonical(self):
        bundle = load("admitted.json")
        bundle["evidence"][0]["derived_index"] = True
        receipt = validate_export(bundle)
        self.assertIn("evidence[0]:derived_index_not_canonical", receipt["reasons"])

    def test_integrity_only_cannot_claim_payload_available(self):
        bundle = load("admitted.json")
        bundle["evidence"][0]["fidelity"] = "integrity_only"
        bundle["evidence"][0]["retention_class"] = "integrity_only"
        receipt = validate_export(bundle)
        self.assertIn("evidence[0]:payload_availability_contradiction", receipt["reasons"])


if __name__ == "__main__":
    unittest.main()
