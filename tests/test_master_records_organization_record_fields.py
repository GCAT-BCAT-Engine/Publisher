import importlib.util
import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "tools" / "check_erl_kv_provider_proof_projection.py"


def _load_check():
    spec = importlib.util.spec_from_file_location("check_erl_kv_provider_proof_projection", CHECK)
    module = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(module)
    return module


class MasterRecordsOrganizationRecordFieldTests(unittest.TestCase):
    def test_projection_emits_only_new_name(self):
        data = json.loads((ROOT / "data" / "erl-kv-provider-proof-projection.json").read_text(encoding="utf-8"))
        self.assertIn("master_records_organization_record_commit", data["upstream"])
        self.assertNotIn("master_records_custody_commit", data["upstream"])
        self.assertIn("master_records_organization_record_reconstructed", data["proof"])

    def test_reader_accepts_new_name(self):
        m = _load_check()
        self.assertEqual(m.organization_record_commit({m.ORGANIZATION_RECORD_COMMIT: "abc"}), "abc")

    def test_reader_accepts_legacy_name(self):
        m = _load_check()
        self.assertEqual(m.organization_record_commit({m.LEGACY_ORGANIZATION_RECORD_COMMIT: "abc"}), "abc")

    def test_new_name_wins_over_legacy(self):
        m = _load_check()
        value = {m.ORGANIZATION_RECORD_COMMIT: "new", m.LEGACY_ORGANIZATION_RECORD_COMMIT: "old"}
        self.assertEqual(m.organization_record_commit(value), "new")


if __name__ == "__main__":
    unittest.main()
