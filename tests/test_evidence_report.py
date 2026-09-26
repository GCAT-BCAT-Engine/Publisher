from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from publisher.evidence_report import EvidenceReportError, render_evidence_report, validate_package


def base_package(status: str = "IN_PROGRESS"):
    return {
        "schema": "stegverse.publisher.evidence-report-package/v1",
        "report_id": "example-evidence-report-001",
        "title": "Example Evidence Report",
        "subtitle": "Reusable Publisher report fixture",
        "authors": ["Example Author"],
        "subject": {
            "name": "Example System",
            "class": "SDK evaluation",
            "version": "1.0.0",
            "source_repo": "example/repo"
        },
        "status": status,
        "abstract": "A bounded example report.",
        "objective_scope": "Demonstrate the generic evidence-report renderer without granting authority.",
        "frozen_parameters": {"manifest_sha256": "abc"},
        "primary_execution": {
            "state": "EXECUTED",
            "summary": "Primary execution completed.",
            "result": "PASS",
            "evidence_refs": ["evidence:primary"]
        },
        "replay": {
            "state": "EXECUTED",
            "summary": "Replay completed.",
            "result": "MATCH",
            "evidence_refs": ["evidence:replay"]
        },
        "reconstruction": {
            "state": "EXECUTED",
            "summary": "Reconstruction completed.",
            "result": "CONSISTENT",
            "evidence_refs": ["evidence:reconstruction"]
        },
        "screenshots": [
            {
                "step_id": "manifest-builder",
                "title": "Manifest Builder",
                "purpose": "Show frozen manifest creation",
                "artifact_ref": "artifact:manifest-builder.png",
                "sha256": "0" * 64,
                "capture_class": "RUNTIME_EVIDENCE",
                "related_ref": "evidence:primary"
            }
        ],
        "conclusion": "The bounded example completed.",
        "evidence_ledger": {"refs": ["evidence:primary", "evidence:replay", "evidence:reconstruction"]},
        "usage_guide": {
            "overview": "Submit a structured evidence package to Publisher.",
            "instructions": ["Build package", "Render package"],
            "worked_example": "python tools/render_evidence_report.py package.json --output-dir out"
        },
        "roadmap": {
            "implemented": ["Deterministic multi-format rendering"],
            "planned": ["Browser-friendly parity surface"],
            "browser_parity_target": "Safely exposable functions should preserve artifact semantics across browser and programmatic paths."
        },
        "requested_formats": ["markdown", "html", "pdf", "docx", "json"],
        "publication_authorized": False,
        "release_authorized": False,
        "execution_authorized": False,
        "authority_effect": "NONE"
    }


class EvidenceReportTests(unittest.TestCase):
    def test_complete_package_renders_all_formats_and_receipt(self):
        package = base_package("COMPLETE")
        with tempfile.TemporaryDirectory() as tmp:
            manifest, receipt = render_evidence_report(package, Path(tmp))
            self.assertEqual(receipt["result"], "GENERATED_VALIDATED_NOT_PUBLISHED")
            self.assertFalse(receipt["publication_authorized"])
            self.assertEqual(receipt["authority_effect"], "NONE")
            self.assertEqual({x["format"] for x in manifest["artifacts"]}, {"markdown", "html", "pdf", "docx", "json"})
            for artifact in manifest["artifacts"]:
                self.assertTrue((Path(tmp) / artifact["path"]).exists())
            self.assertTrue((Path(tmp) / "artifact-manifest.json").exists())
            self.assertTrue((Path(tmp) / "rendering-receipt.json").exists())

    def test_complete_rejects_unexecuted_replay(self):
        package = base_package("COMPLETE")
        package["replay"] = {"state": "NOT_RUN", "summary": "", "result": "", "evidence_refs": []}
        with self.assertRaisesRegex(EvidenceReportError, "unexecuted stages"):
            validate_package(package)

    def test_in_progress_may_render_with_unexecuted_stage(self):
        package = base_package("IN_PROGRESS")
        package["replay"] = {"state": "NOT_RUN", "summary": "Pending", "result": "", "evidence_refs": []}
        validate_package(package)

    def test_executed_stage_requires_evidence_reference(self):
        package = base_package()
        package["primary_execution"]["evidence_refs"] = []
        with self.assertRaisesRegex(EvidenceReportError, "executed without evidence refs"):
            validate_package(package)

    def test_authority_expansion_rejected(self):
        package = base_package()
        package["publication_authorized"] = True
        with self.assertRaisesRegex(EvidenceReportError, "publication_authorized must be false"):
            validate_package(package)

    def test_duplicate_screenshot_step_rejected(self):
        package = base_package()
        package["screenshots"].append(dict(package["screenshots"][0]))
        with self.assertRaisesRegex(EvidenceReportError, "duplicate"):
            validate_package(package)


if __name__ == "__main__":
    unittest.main()
