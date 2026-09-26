"""General, non-authorizing Publisher evidence-report rendering."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from publisher.document_pipeline import (
    render_docx,
    render_html,
    render_json,
    render_markdown,
    render_pdf,
)

PACKAGE_SCHEMA = "stegverse.publisher.evidence-report-package/v1"
MANIFEST_SCHEMA = "stegverse.publisher.evidence-report-artifact-manifest/v1"
RECEIPT_SCHEMA = "stegverse.publisher.evidence-report-rendering-receipt/v1"
RENDERER_VERSION = "publisher-evidence-report/1.0.0"
FORMATS = {
    "markdown": ("md", render_markdown),
    "html": ("html", render_html),
    "pdf": ("pdf", render_pdf),
    "docx": ("docx", render_docx),
    "json": ("json", render_json),
}


class EvidenceReportError(ValueError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def package_digest(package: dict[str, Any]) -> str:
    return sha256_hex(canonical_json(package).encode("utf-8"))


def validate_package(package: dict[str, Any]) -> None:
    if not isinstance(package, dict) or package.get("schema") != PACKAGE_SCHEMA:
        raise EvidenceReportError("evidence report package schema mismatch")
    if package.get("authority_effect") != "NONE":
        raise EvidenceReportError("authority effect must remain NONE")
    for field in ("publication_authorized", "release_authorized", "execution_authorized"):
        if package.get(field) is not False:
            raise EvidenceReportError(f"{field} must be false")
    if not isinstance(package.get("report_id"), str) or not package["report_id"]:
        raise EvidenceReportError("report_id required")
    if not isinstance(package.get("title"), str) or not package["title"]:
        raise EvidenceReportError("title required")
    requested = package.get("requested_formats")
    if not isinstance(requested, list) or not requested or len(requested) != len(set(requested)):
        raise EvidenceReportError("requested_formats invalid")
    if not set(requested).issubset(FORMATS):
        raise EvidenceReportError("requested format unsupported")

    for name in ("primary_execution", "replay", "reconstruction"):
        stage = package.get(name)
        if not isinstance(stage, dict) or stage.get("state") not in {"NOT_RUN", "UNAVAILABLE", "EXECUTED"}:
            raise EvidenceReportError(f"{name} stage invalid")
        if not isinstance(stage.get("evidence_refs"), list):
            raise EvidenceReportError(f"{name} evidence_refs invalid")
        if stage["state"] == "EXECUTED" and not stage["evidence_refs"]:
            raise EvidenceReportError(f"{name} executed without evidence refs")

    screenshots = package.get("screenshots")
    if not isinstance(screenshots, list):
        raise EvidenceReportError("screenshots must be a list")
    seen_steps: set[str] = set()
    for index, shot in enumerate(screenshots):
        if not isinstance(shot, dict):
            raise EvidenceReportError(f"screenshot[{index}] invalid")
        step = shot.get("step_id")
        if not isinstance(step, str) or not step or step in seen_steps:
            raise EvidenceReportError(f"screenshot[{index}] step invalid or duplicate")
        seen_steps.add(step)
        digest = shot.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            raise EvidenceReportError(f"screenshot[{index}] sha256 invalid")
        try:
            int(digest, 16)
        except ValueError as exc:
            raise EvidenceReportError(f"screenshot[{index}] sha256 invalid") from exc

    if package.get("status") == "COMPLETE":
        incomplete = [
            name for name in ("primary_execution", "replay", "reconstruction")
            if package[name]["state"] != "EXECUTED"
        ]
        if incomplete:
            raise EvidenceReportError("complete report has unexecuted stages: " + ",".join(incomplete))
        if not screenshots:
            raise EvidenceReportError("complete report requires screenshot evidence")


def _json_block(value: Any) -> str:
    return "```json\n" + json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n```"


def build_document_model(package: dict[str, Any]) -> dict[str, Any]:
    validate_package(package)
    authors = [{"name": name} for name in package.get("authors", [])] or [{"name": "StegVerse Publisher"}]
    sections: list[dict[str, Any]] = []

    def add(section_id: str, heading: str, body: str, refs: list[str] | None = None) -> None:
        sections.append({
            "section_id": section_id,
            "heading": heading,
            "body": body,
            "content_class": "OWNER_AUTHORED",
            "fidelity": "semantic_reconstruction",
            "source_subject_ids": refs or [],
        })

    add("abstract", "Abstract", package["abstract"])
    add("objective-scope", "Test Objective and Scope", package["objective_scope"])
    add("frozen-parameters", "Frozen Test Parameters", _json_block(package["frozen_parameters"]))

    for key, heading in (
        ("primary_execution", "Primary Test Execution and Result"),
        ("replay", "Replay and Result"),
        ("reconstruction", "Reconstruction and Result"),
    ):
        stage = package[key]
        body = (
            f"State: {stage['state']}\n\n"
            f"{stage.get('summary', '')}\n\n"
            f"Result: {stage.get('result', '')}\n\n"
            f"Evidence references:\n" + "\n".join(f"- {ref}" for ref in stage.get("evidence_refs", []))
        )
        add(key, heading, body)

    shot_lines = []
    for shot in package["screenshots"]:
        shot_lines.extend([
            f"### {shot['title']}",
            f"Step: {shot['step_id']}",
            f"Purpose: {shot['purpose']}",
            f"Capture class: {shot['capture_class']}",
            f"Artifact: {shot['artifact_ref']}",
            f"SHA-256: {shot['sha256']}",
            f"Related reference: {shot.get('related_ref', '')}",
            "",
        ])
    add("screenshots", "Screenshot Walkthrough", "\n".join(shot_lines) if shot_lines else "No screenshots retained yet.")
    add("conclusion", "Conclusion", package["conclusion"])
    add("appendix-a", "Appendix A — Evidence Ledger", _json_block(package["evidence_ledger"]))

    guide = package["usage_guide"]
    guide_body = guide["overview"] + "\n\nInstructions:\n" + "\n".join(
        f"{idx}. {item}" for idx, item in enumerate(guide["instructions"], start=1)
    )
    if guide.get("worked_example"):
        guide_body += "\n\nWorked example:\n" + guide["worked_example"]
    add("appendix-b", "Appendix B — SDK / Function Overview and Usage Guide", guide_body)

    roadmap = package["roadmap"]
    roadmap_body = "Implemented:\n" + "\n".join(f"- {item}" for item in roadmap.get("implemented", []))
    roadmap_body += "\n\nPlanned:\n" + "\n".join(f"- {item}" for item in roadmap.get("planned", []))
    if roadmap.get("browser_parity_target"):
        roadmap_body += "\n\nBrowser parity target:\n" + roadmap["browser_parity_target"]
    add("appendix-c", "Appendix C — Roadmap and Future Development", roadmap_body)

    digest = package_digest(package)
    return {
        "schema_version": "stegverse.publisher.document/v1",
        "renderer_version": RENDERER_VERSION,
        "document": {
            "document_id": package["report_id"],
            "title": package["title"],
            "subtitle": package.get("subtitle", ""),
            "authors": authors,
            "sections": sections,
        },
        "evidence": [],
        "source_binding": {
            "export_id": package["report_id"],
            "export_sha256": "sha256:" + digest,
            "source_repository": package.get("subject", {}).get("source_repo", ""),
            "source_release": package.get("subject", {}).get("version", ""),
            "vault_class": None,
            "verification_root": "sha256:" + digest,
            "event_ids": [],
            "authority_ref": "publisher-evidence-report/non-authorizing",
            "redaction_profile": "package-defined",
        },
        "lifecycle": {
            "state": "GENERATED_VALIDATED_NOT_PUBLISHED",
            "publication_authorized": False,
            "release_authorized": False,
            "execution_authorized": False,
            "authority_effect": "NONE",
        },
    }


def render_evidence_report(package: dict[str, Any], output_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    model = build_document_model(package)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = []
    for fmt in package["requested_formats"]:
        ext, renderer = FORMATS[fmt]
        data = renderer(model)
        path = output_dir / f"{package['report_id']}.{ext}"
        path.write_bytes(data)
        artifacts.append({
            "format": fmt,
            "path": path.name,
            "sha256": sha256_hex(data),
            "size_bytes": len(data),
        })

    manifest_core = {
        "schema": MANIFEST_SCHEMA,
        "report_id": package["report_id"],
        "package_sha256": package_digest(package),
        "renderer_version": RENDERER_VERSION,
        "artifacts": artifacts,
        "lifecycle_state": "GENERATED_VALIDATED_NOT_PUBLISHED",
        "authority_effect": "NONE",
    }
    manifest = dict(manifest_core)
    manifest["manifest_sha256"] = sha256_hex(canonical_json(manifest_core).encode("utf-8"))
    (output_dir / "artifact-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    receipt = {
        "schema": RECEIPT_SCHEMA,
        "report_id": package["report_id"],
        "result": "GENERATED_VALIDATED_NOT_PUBLISHED",
        "package_sha256": manifest["package_sha256"],
        "manifest_sha256": manifest["manifest_sha256"],
        "publication_authorized": False,
        "release_authorized": False,
        "execution_authorized": False,
        "authority_effect": "NONE",
    }
    (output_dir / "rendering-receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest, receipt
