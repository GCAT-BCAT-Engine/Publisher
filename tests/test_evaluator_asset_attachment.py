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
    verify_artifact_return, sha256_value,
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



def generic_review_transfer():
    value = transfer()
    originals_list = originals()
    b = value["export_bundle"]
    b["schema_version"] = "stegverse.publisher.evidence-report-package/v1"
    b["export_id"] = "sdk-review-generic-positive-fixture"
    b["source"]["repository"] = "StegVerse-org/StegVerse-SDK"
    b["source"]["release"] = "SDK-manifest-source-fixture"
    b["source"]["event_ids"] = [item["path"] for item in originals_list]
    b["authorization"]["purpose"] = "EXTERNAL_EVALUATOR_REVIEW"
    b["authorization"]["authority_ref"] = "direct-user-review-instruction-fixture"
    b["authorization"]["scope"] = [item["path"] for item in originals_list]
    b["evidence"] = [
        {
            "subject_id": item["path"], "path": item["path"],
            "content_hash": item["sha256"], "bytes": item["bytes"],
            "media_type": item["media_type"], "fidelity": "exact",
            "retention_class": "full_fidelity", "payload_available": True,
            "derived_index": False, "superseded": False, "restricted": False,
            "contains_credentials": False,
        } for item in originals_list
    ]
    b["document"]["document_id"] = "mir-sv-exp3-generic-source-fixture"
    b["document"]["title"] = "Independent capabilities and limits"
    b["document"]["sections"] = [
        {
            "section_id": name, "heading": name.title(),
            "body": "Claimed source capability is distinct from current authentic observations. The limitation is in this same section.",
            "content_class": "OWNER_AUTHORED", "fidelity": "semantic_reconstruction",
            "source_subject_ids": [originals_list[0]["path"]],
        } for name in ("observe","demonstrate","retain","reconstruct")
    ]
    unhashed = copy.deepcopy(b)
    unhashed.pop("export_sha256")
    b["export_sha256"] = sha256_value(unhashed)
    value["export_sha256"] = b["export_sha256"]
    value["authorization_ref"] = b["authorization"]["authority_ref"]
    value["evaluator_assets"] = originals_list
    return value


class GenericReviewTransferTests(unittest.TestCase):
    def test_generic_evaluator_bundle_admitted_on_existing_publisher(self):
        value = generic_review_transfer()
        with tempfile.TemporaryDirectory() as td:
            produced, returned = process_artifact_transfer(canonical_json(value).encode(), Path(td))
            verified = verify_artifact_return(returned)
            self.assertEqual(produced, verified)
            self.assertEqual(len([x for x in verified["artifacts"] if x["format"] == "source-original"]), 2)
            self.assertEqual(verified["rendering_receipt"]["result"], "GENERATED_VALIDATED_NOT_PUBLISHED")
            self.assertNotIn("roundtrip_binding", verified)
            self.assertFalse(verified["publication_authorized"])

    def test_generic_evaluator_bundle_cannot_omit_original(self):
        value = generic_review_transfer()
        value["evaluator_assets"].pop()
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(EvaluatorAssetError, "coverage mismatch"):
                process_artifact_transfer(canonical_json(value).encode(), Path(td))

    def test_generic_evaluator_mismatched_inventory_sha_rejected(self):
        value = generic_review_transfer()
        value["export_bundle"]["evidence"][0]["content_hash"] = "sha256:" + "0"*64
        unhashed = copy.deepcopy(value["export_bundle"])
        unhashed.pop("export_sha256")
        value["export_bundle"]["export_sha256"] = sha256_value(unhashed)
        value["export_sha256"] = value["export_bundle"]["export_sha256"]
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(EvaluatorAssetError, "inventory does not match"):
                process_artifact_transfer(canonical_json(value).encode(), Path(td))


if __name__ == "__main__":
    unittest.main()
