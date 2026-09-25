"""Reusable source-original evaluator attachment tests on existing Publisher."""
from __future__ import annotations
import base64
import copy
import json
import tempfile
import unittest
from pathlib import Path

from publisher.evaluator_asset_attachment import EvaluatorAssetError, parse_assets, sha
from publisher.intr_artifact_transfer import (
    PublisherArtifactTransferError, canonical_json, process_artifact_transfer,
    verify_artifact_return,
)
from tests.test_intr_artifact_transfer import transfer


def originals():
    pdf = b"%PDF-1.4\n% original counterpart supplied by experiment partner\n"
    png = b"\x89PNG\r\n\x1a\nfixture retained exact original bytes"
    return [
        {"path": "evidence/original.pdf", "media_type": "application/pdf",
         "sha256": sha(pdf), "bytes": len(pdf), "content_base64": base64.b64encode(pdf).decode(),
         "source_class": "COUNTERPART_SUPPLIED_ORIGINAL"},
        {"path": "evidence/IMG_3282.png", "media_type": "image/png",
         "sha256": sha(png), "bytes": len(png), "content_base64": base64.b64encode(png).decode(),
         "source_class": "USER_SUPPLIED_ORIGINAL"},
    ]


class EvaluatorAssetsTests(unittest.TestCase):
    def test_existing_generic_transfer_returns_every_original_exactly(self):
        value = transfer()
        value["evaluator_assets"] = originals()
        with tempfile.TemporaryDirectory() as td:
            parsed, raw = process_artifact_transfer(canonical_json(value).encode(), Path(td))
            verified = verify_artifact_return(raw)
            self.assertEqual(verified, parsed)
            for original in originals():
                stored = (Path(td) / original["path"]).read_bytes()
                self.assertEqual(stored, base64.b64decode(original["content_base64"]))
                self.assertEqual(sha(stored), original["sha256"])
                self.assertEqual(
                    next(x for x in verified["artifacts"] if x["path"] == original["path"])["content_base64"],
                    original["content_base64"],
                )
            self.assertEqual(len(verified["artifacts"]), len(value["requested_formats"]) + 2)
            self.assertFalse(verified["publication_authorized"])
            self.assertFalse(verified["release_authorized"])

    def test_missing_original_fails_closed(self):
        value = transfer()
        value["evaluator_assets"] = originals()
        with tempfile.TemporaryDirectory() as td:
            _, raw = process_artifact_transfer(canonical_json(value).encode(), Path(td))
        broken = json.loads(raw)
        broken["artifacts"] = [a for a in broken["artifacts"] if a["path"] != "evidence/IMG_3282.png"]
        with self.assertRaisesRegex(PublisherArtifactTransferError, "coverage mismatch"):
            verify_artifact_return(canonical_json(broken).encode())

    def test_mutated_original_fails(self):
        value = originals()
        value[1]["content_base64"] = base64.b64encode(b"\x89PNG\r\n\x1a\nchanged").decode()
        with self.assertRaisesRegex(EvaluatorAssetError, "hash/size mismatch"):
            parse_assets(value)

    def test_path_escape_and_duplicate_rejected(self):
        value = originals()
        value[0]["path"] = "../outside.pdf"
        with self.assertRaisesRegex(EvaluatorAssetError, "unsafe"):
            parse_assets(value)
        value = originals()
        value[1]["path"] = value[0]["path"]
        with self.assertRaisesRegex(EvaluatorAssetError, "unsafe/duplicate"):
            parse_assets(value)

    def test_augmented_manifest_or_receipt_tampering_rejected(self):
        value = transfer()
        value["evaluator_assets"] = originals()
        with tempfile.TemporaryDirectory() as td:
            _, raw = process_artifact_transfer(canonical_json(value).encode(), Path(td))
        for location in ("manifest", "rendering_receipt"):
            broken = json.loads(raw)
            broken[location]["generation_id"] = "changed"
            with self.subTest(location=location):
                with self.assertRaisesRegex(PublisherArtifactTransferError, "digest mismatch"):
                    verify_artifact_return(canonical_json(broken).encode())

    def test_optional_when_not_declared(self):
        raw = canonical_json(transfer()).encode()
        with tempfile.TemporaryDirectory() as td:
            _, ret = process_artifact_transfer(raw, Path(td))
        self.assertTrue(verify_artifact_return(ret))
        self.assertEqual(parse_assets(originals())[0][0]["path"], "evidence/original.pdf")


if __name__ == "__main__":
    unittest.main()
