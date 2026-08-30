from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest
import zipfile

from publisher.document_pipeline import (
    DocumentPipelineError,
    canonical_json,
    render_document_bundle,
    sha256_uri,
    validate_document_bundle,
    verify_artifact_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "document-export" / "admitted.json"


class DocumentPipelineTests(unittest.TestCase):
    def setUp(self):
        self.bundle = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.now = datetime(2026, 8, 29, 8, 30, tzinfo=timezone.utc)

    @staticmethod
    def rehash(bundle):
        value = copy.deepcopy(bundle)
        value.pop("export_sha256", None)
        bundle["export_sha256"] = sha256_uri(value)

    def test_renders_and_verifies_all_authorized_formats(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            manifest, receipt = render_document_bundle(self.bundle, output, now=self.now)
            self.assertEqual(
                {item["format"] for item in manifest["artifacts"]},
                {"markdown", "html", "pdf", "docx", "json"},
            )
            self.assertTrue(verify_artifact_manifest(output, manifest))
            self.assertEqual(receipt["result"], "GENERATED_VALIDATED_NOT_PUBLISHED")
            self.assertFalse(receipt["publication_authorized"])
            self.assertEqual(receipt["authority_effect"], "NONE")
            self.assertTrue((output / "project-brief-demo-001.pdf").read_bytes().startswith(b"%PDF-1.4"))
            with zipfile.ZipFile(output / "project-brief-demo-001.docx") as archive:
                self.assertIn("word/document.xml", archive.namelist())

    def test_pipeline_is_deterministic_for_same_bundle(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            manifest1, receipt1 = render_document_bundle(self.bundle, Path(first), now=self.now)
            manifest2, receipt2 = render_document_bundle(self.bundle, Path(second), now=self.now)
            self.assertEqual(manifest1, manifest2)
            self.assertEqual(receipt1, receipt2)
            for item in manifest1["artifacts"]:
                self.assertEqual((Path(first) / item["path"]).read_bytes(), (Path(second) / item["path"]).read_bytes())

    def test_tampered_source_bundle_hash_fails_closed(self):
        bundle = copy.deepcopy(self.bundle)
        bundle["document"]["title"] = "Tampered"
        with self.assertRaisesRegex(DocumentPipelineError, "hash mismatch"):
            validate_document_bundle(bundle, now=self.now)

    def test_revoked_or_expired_bundle_fails_closed(self):
        revoked = copy.deepcopy(self.bundle)
        revoked["authorization"]["revoked"] = True
        self.rehash(revoked)
        with self.assertRaises(DocumentPipelineError):
            validate_document_bundle(revoked, now=self.now)
        expired = copy.deepcopy(self.bundle)
        expired["authorization"]["expires_at"] = "2026-08-29T08:29:59Z"
        self.rehash(expired)
        with self.assertRaisesRegex(DocumentPipelineError, "expired"):
            validate_document_bundle(expired, now=self.now)

    def test_restricted_source_is_rejected_by_existing_admission_gate(self):
        bundle = copy.deepcopy(self.bundle)
        bundle["evidence"][0]["restricted"] = True
        self.rehash(bundle)
        with self.assertRaisesRegex(DocumentPipelineError, "restricted_content"):
            validate_document_bundle(bundle, now=self.now)

    def test_ai_derived_exact_claim_is_rejected(self):
        bundle = copy.deepcopy(self.bundle)
        bundle["document"]["sections"][1]["fidelity"] = "exact"
        self.rehash(bundle)
        with self.assertRaisesRegex(DocumentPipelineError, "AI-derived exact"):
            validate_document_bundle(bundle, now=self.now)

    def test_unknown_content_class_and_missing_provenance_fail_closed(self):
        unknown = copy.deepcopy(self.bundle)
        unknown["document"]["sections"][0]["content_class"] = "MODEL_TRUTH"
        self.rehash(unknown)
        with self.assertRaisesRegex(DocumentPipelineError, "content class"):
            validate_document_bundle(unknown, now=self.now)
        unbound = copy.deepcopy(self.bundle)
        unbound["document"]["sections"][1]["source_subject_ids"] = []
        self.rehash(unbound)
        with self.assertRaisesRegex(DocumentPipelineError, "source provenance"):
            validate_document_bundle(unbound, now=self.now)

    def test_artifact_manifest_detects_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            manifest, _ = render_document_bundle(self.bundle, output, now=self.now)
            artifact = output / manifest["artifacts"][0]["path"]
            artifact.write_bytes(artifact.read_bytes() + b"tamper")
            self.assertFalse(verify_artifact_manifest(output, manifest))

    def test_immutable_artifact_conflict_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            render_document_bundle(self.bundle, output, now=self.now)
            path = output / "project-brief-demo-001.md"
            path.write_text("different", encoding="utf-8")
            with self.assertRaisesRegex(DocumentPipelineError, "immutable artifact conflict"):
                render_document_bundle(self.bundle, output, now=self.now)


if __name__ == "__main__":
    unittest.main()
