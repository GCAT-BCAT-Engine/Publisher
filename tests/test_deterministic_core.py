"""publication_plane.core.deterministic: the in-repo copy of stegverse-core-lite's hashing and receipt IDs.

Standard library only (unittest). Each golden value is also recomputed here straight from hashlib, so the vectors do
not depend on the module under test. Goal StegVerse-org/.github#164 (dependency reduction)."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from publication_plane.core.deterministic import (  # noqa: E402
    DeterministicHash, DeterministicReceiptID, ReceiptIDProvider)
from publication_plane.core.receipt_writer import PublicationReceiptWriter  # noqa: E402

DOC = {"gate_result": "ALLOW", "confidence": 0.947, "module": "publisher",
       "nested": {"b": [1, 2, {"é": "✓"}], "a": None}}


def oracle(content: str, seed: str) -> str:
    return hashlib.sha256(f"{content}::{seed}".encode("utf-8")).hexdigest()


class DeterministicCoreTests(unittest.TestCase):
    def test_golden_vectors_match_hashlib(self):
        canon = json.dumps(DOC, sort_keys=True, ensure_ascii=True)
        cases = {
            ("test content", "demo-seed-001"): "12cf36f3e7960314bc8774e2e1fb355d6976b6c3399b812f5420b269d43a1073",
            ("", ""): "71546855d6279ef70d20909b292c42c2dcb02cd06bde01485da52d13e304ebf4",
            ("ünïcødé ✓", "s"): "055dce16971f689fcd054d2bd003935e83eb795558c60eb0af08aa912af6219a",
        }
        for (content, seed), want in cases.items():
            with self.subTest(content=content):
                self.assertEqual(oracle(content, seed), want)
                self.assertEqual(DeterministicHash.hash(content, seed), want)
        self.assertEqual(DeterministicHash.hash_dict(DOC, "run-001"), oracle(canon, "run-001"))
        self.assertEqual(DeterministicHash.hash_dict(DOC, "run-001"),
                         "aecdaacf701555d31f179e73986f1dfdd6aa29b85c1a715629210b72d1d8bf61")
        full = oracle(canon, "publisher-default-seed")
        self.assertEqual(DeterministicReceiptID().derive_full(DOC, "publisher-default-seed"), full)
        self.assertEqual(DeterministicReceiptID().derive(DOC, "publisher-default-seed"), full[:32])
        self.assertEqual(full[:32], "cce807e5468cc8351f9322c4fae25b95")

    def test_verify_detects_tamper_and_protocol_holds(self):
        rid = DeterministicReceiptID()
        receipt = rid.derive(DOC, "seed")
        self.assertTrue(rid.verify(receipt, DOC, "seed"))
        self.assertFalse(rid.verify(receipt, dict(DOC, confidence=0.5), "seed"))
        self.assertFalse(rid.verify(receipt, DOC, "other-seed"))
        self.assertIsInstance(rid, ReceiptIDProvider)

    def test_receipt_writer_round_trip_needs_no_external_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            writer = PublicationReceiptWriter(seed="s", output_dir=tmp)
            path = writer.write("ALLOW", 0.9, {"k": "v"}, "m", "d")
            self.assertTrue(writer.verify(path))
            doc = json.loads(path.read_text(encoding="utf-8"))
            doc["gate_result"] = "DENY"
            path.write_text(json.dumps(doc), encoding="utf-8")
            self.assertFalse(writer.verify(path))

    def test_no_module_imports_stegverse_core_lite(self):
        hits = []
        for base in ("src", "publisher", "tools", "tests"):
            for py in (ROOT / base).rglob("*.py"):
                if py.resolve() == Path(__file__).resolve():
                    continue
                text = py.read_text(encoding="utf-8", errors="replace")
                if "import stegverse_core_lite" in text or "from stegverse_core_lite" in text:
                    hits.append(str(py.relative_to(ROOT)))
        self.assertEqual(hits, [])
        self.assertNotIn("stegverse-core-lite", (ROOT / "pyproject.toml").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
