"""Governed, dependency-light document rendering for KnowledgeVault exports."""
from __future__ import annotations

import copy
import hashlib
import html
import io
import json
import re
import textwrap
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from publisher.continuity_recall_admission import validate_export


BUNDLE_SCHEMA = "stegverse.kv.publisher-document-export/v1"
DOCUMENT_SCHEMA = "stegverse.publisher.document/v1"
MANIFEST_SCHEMA = "stegverse.publisher.document-artifact-manifest/v1"
RECEIPT_SCHEMA = "stegverse.publisher.document-rendering-receipt/v1"
RENDERER_VERSION = "publisher-document-pipeline/1.0.0"
FORMATS = {"markdown", "html", "pdf", "docx", "json"}
CONTENT_CLASSES = {"RAW_SOURCE_EXCERPT", "OWNER_AUTHORED", "AI_DERIVED"}
FIDELITIES = {"exact", "semantic_reconstruction", "inference"}
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,127}$")


class DocumentPipelineError(ValueError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_uri(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _parse_time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise DocumentPipelineError("invalid timestamp") from exc
    if parsed.tzinfo is None:
        raise DocumentPipelineError("timestamp must include timezone")
    return parsed.astimezone(timezone.utc)


def _verify_bundle_hash(bundle: dict[str, Any]) -> None:
    expected = bundle.get("export_sha256")
    unhashed = copy.deepcopy(bundle)
    unhashed.pop("export_sha256", None)
    if expected != sha256_uri(unhashed):
        raise DocumentPipelineError("KV export hash mismatch")


def _legacy_admission_projection(bundle: dict[str, Any]) -> dict[str, Any]:
    """Project the v1 document bundle into the existing recall-admission gate."""
    projected = copy.deepcopy(bundle)
    root = projected.get("source", {}).get("verification_root")
    if isinstance(root, str) and root.startswith("sha256:"):
        projected["source"]["verification_root"] = root[7:]
    for item in projected.get("evidence", []):
        digest = item.get("content_hash")
        if isinstance(digest, str) and digest.startswith("sha256:"):
            item["content_hash"] = digest[7:]
    return projected


def validate_document_bundle(bundle: dict[str, Any], *, now: datetime | None = None) -> dict[str, Any]:
    if not isinstance(bundle, dict) or bundle.get("schema_version") != BUNDLE_SCHEMA:
        raise DocumentPipelineError("document bundle schema mismatch")
    _verify_bundle_hash(bundle)
    admission = validate_export(_legacy_admission_projection(bundle))
    if admission.get("result") != "ADMITTED":
        raise DocumentPipelineError("continuity export rejected: " + ",".join(admission.get("reasons", [])))
    if any(bundle.get(flag) is not False for flag in ("publication_authorized", "release_authorized", "execution_authorized")):
        raise DocumentPipelineError("KV bundle attempts authority expansion")
    if bundle.get("authority_effect") != "NONE":
        raise DocumentPipelineError("KV bundle authority effect invalid")
    auth = bundle["authorization"]
    if auth.get("revoked") is not False or auth.get("status") != "active":
        raise DocumentPipelineError("export authorization inactive")
    expires = auth.get("expires_at")
    if expires is not None and _parse_time(expires) <= (now or datetime.now(timezone.utc)).astimezone(timezone.utc):
        raise DocumentPipelineError("export authorization expired")
    requested = bundle.get("requested_formats")
    allowed = auth.get("allowed_formats")
    if (
        not isinstance(requested, list)
        or not requested
        or len(requested) != len(set(requested))
        or not set(requested).issubset(FORMATS)
        or not isinstance(allowed, list)
        or not set(requested).issubset(set(allowed))
    ):
        raise DocumentPipelineError("format authorization invalid")
    redaction = bundle.get("redaction")
    if (
        not isinstance(redaction, dict)
        or redaction.get("review_state") != "OWNER_APPROVED"
        or redaction.get("restricted_content_present") is not False
    ):
        raise DocumentPipelineError("owner-approved redaction missing")
    document = bundle.get("document")
    if not isinstance(document, dict) or not SAFE_ID.fullmatch(str(document.get("document_id", ""))):
        raise DocumentPipelineError("safe document id required")
    if not isinstance(document.get("title"), str) or not document["title"]:
        raise DocumentPipelineError("document title required")
    if not isinstance(document.get("authors"), list) or not document["authors"] or any(
        not isinstance(author, dict) or not isinstance(author.get("name"), str) or not author["name"]
        for author in document.get("authors", [])
    ):
        raise DocumentPipelineError("document authors required")
    evidence_ids = {item.get("subject_id") for item in bundle.get("evidence", [])}
    sections = document.get("sections")
    if not isinstance(sections, list) or not sections:
        raise DocumentPipelineError("document sections required")
    section_ids: set[str] = set()
    for index, section in enumerate(sections):
        if not isinstance(section, dict):
            raise DocumentPipelineError(f"section[{index}] invalid")
        section_id = section.get("section_id")
        if not isinstance(section_id, str) or not section_id or section_id in section_ids:
            raise DocumentPipelineError(f"section[{index}] id invalid or duplicate")
        section_ids.add(section_id)
        if any(not isinstance(section.get(field), str) or not section[field] for field in ("heading", "body", "content_class", "fidelity")):
            raise DocumentPipelineError(f"section[{index}] incomplete")
        refs = section.get("source_subject_ids")
        if not isinstance(refs, list) or not set(refs).issubset(evidence_ids):
            raise DocumentPipelineError(f"section[{index}] source provenance invalid")
        if section["content_class"] not in CONTENT_CLASSES or section["fidelity"] not in FIDELITIES:
            raise DocumentPipelineError(f"section[{index}] content class or fidelity invalid")
        if section["content_class"] != "OWNER_AUTHORED" and not refs:
            raise DocumentPipelineError(f"section[{index}] source provenance invalid")
        if section["content_class"] == "RAW_SOURCE_EXCERPT" and section["fidelity"] != "exact":
            raise DocumentPipelineError(f"section[{index}] raw excerpt must retain exact fidelity")
        if section["content_class"] == "AI_DERIVED" and section["fidelity"] == "exact":
            raise DocumentPipelineError(f"section[{index}] AI-derived exact claim prohibited")
        if section["content_class"] == "AI_DERIVED" and not isinstance(section.get("confidence"), (int, float)):
            raise DocumentPipelineError(f"section[{index}] AI-derived confidence required")
    return admission


def build_canonical_document(bundle: dict[str, Any]) -> dict[str, Any]:
    """Construct the renderer-neutral PublisherDocument projection."""
    return {
        "schema_version": DOCUMENT_SCHEMA,
        "renderer_version": RENDERER_VERSION,
        "document": copy.deepcopy(bundle["document"]),
        "evidence": copy.deepcopy(bundle["evidence"]),
        "source_binding": {
            "export_id": bundle["export_id"],
            "export_sha256": bundle["export_sha256"],
            "source_repository": bundle["source"]["repository"],
            "source_release": bundle["source"]["release"],
            "vault_class": bundle["source"].get("vault_class"),
            "verification_root": bundle["source"]["verification_root"],
            "event_ids": copy.deepcopy(bundle["source"]["event_ids"]),
            "authority_ref": bundle["authorization"]["authority_ref"],
            "redaction_profile": bundle["redaction"]["profile"],
        },
        "lifecycle": {
            "state": "ADMITTED_FOR_RENDERING",
            "publication_authorized": False,
            "release_authorized": False,
            "execution_authorized": False,
            "authority_effect": "NONE",
        },
    }


def _authors(document: dict[str, Any]) -> str:
    return ", ".join(author["name"] for author in document["authors"])


def _provenance_lines(model: dict[str, Any]) -> list[str]:
    binding = model["source_binding"]
    return [
        f"Source export: {binding['export_id']}",
        f"Export hash: {binding['export_sha256']}",
        f"Verification root: {binding['verification_root']}",
        "Publication authorized: false",
    ]


def render_markdown(model: dict[str, Any]) -> bytes:
    document = model["document"]
    lines = [f"# {document['title']}", ""]
    if document.get("subtitle"):
        lines.extend([f"_{document['subtitle']}_", ""])
    lines.extend([f"Authors: {_authors(document)}", ""])
    for section in document["sections"]:
        lines.extend([
            f"## {section['heading']}",
            "",
            section["body"],
            "",
            f"> Content class: `{section['content_class']}` · Fidelity: `{section['fidelity']}`"
            + (f" · Confidence: `{section['confidence']:.3f}`" if section.get("confidence") is not None else ""),
            f"> Sources: {', '.join(section['source_subject_ids']) or 'owner-authored'}",
            "",
        ])
    lines.extend(["## Provenance", "", *[f"- {line}" for line in _provenance_lines(model)], ""])
    return "\n".join(lines).encode("utf-8")


def render_html(model: dict[str, Any]) -> bytes:
    document = model["document"]
    sections = []
    for section in document["sections"]:
        confidence = "" if section.get("confidence") is None else f" · Confidence {section['confidence']:.3f}"
        sections.append(
            "<section><h2>" + html.escape(section["heading"]) + "</h2>"
            + "<p>" + html.escape(section["body"]).replace("\n", "<br>") + "</p>"
            + "<aside>Content class: " + html.escape(section["content_class"])
            + " · Fidelity: " + html.escape(section["fidelity"]) + html.escape(confidence)
            + " · Sources: " + html.escape(", ".join(section["source_subject_ids"]) or "owner-authored") + "</aside></section>"
        )
    provenance = "".join("<li>" + html.escape(line) + "</li>" for line in _provenance_lines(model))
    value = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<style>body{{font:16px/1.55 system-ui,sans-serif;max-width:800px;margin:3rem auto;padding:0 1.2rem;color:#172033}}h1,h2{{color:#102a43}}aside{{background:#eef7fa;border-left:4px solid #2c9bc5;padding:.7rem;font-size:.9rem}}footer{{margin-top:3rem;border-top:1px solid #ccd6df}}</style></head>
<body><header><h1>{title}</h1>{subtitle}<p>Authors: {authors}</p></header>{sections}
<footer><h2>Provenance</h2><ul>{provenance}</ul></footer></body></html>""".format(
        title=html.escape(document["title"]),
        subtitle=("<p><em>" + html.escape(document["subtitle"]) + "</em></p>") if document.get("subtitle") else "",
        authors=html.escape(_authors(document)),
        sections="".join(sections),
        provenance=provenance,
    )
    return value.encode("utf-8")


def render_json(model: dict[str, Any]) -> bytes:
    return (json.dumps(model, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def _xml_paragraph(text: str, *, style: str | None = None) -> str:
    style_xml = "" if style is None else f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>'
    return f'<w:p>{style_xml}<w:r><w:t xml:space="preserve">{html.escape(text)}</w:t></w:r></w:p>'


def render_docx(model: dict[str, Any]) -> bytes:
    document = model["document"]
    paragraphs = [_xml_paragraph(document["title"], style="Title")]
    if document.get("subtitle"):
        paragraphs.append(_xml_paragraph(document["subtitle"], style="Subtitle"))
    paragraphs.append(_xml_paragraph("Authors: " + _authors(document)))
    for section in document["sections"]:
        paragraphs.append(_xml_paragraph(section["heading"], style="Heading1"))
        for line in section["body"].splitlines() or [""]:
            paragraphs.append(_xml_paragraph(line))
        marker = f"Content class: {section['content_class']} | Fidelity: {section['fidelity']}"
        if section.get("confidence") is not None:
            marker += f" | Confidence: {section['confidence']:.3f}"
        paragraphs.append(_xml_paragraph(marker))
        paragraphs.append(_xml_paragraph("Sources: " + (", ".join(section["source_subject_ids"]) or "owner-authored")))
    paragraphs.append(_xml_paragraph("Provenance", style="Heading1"))
    paragraphs.extend(_xml_paragraph(line) for line in _provenance_lines(model))
    document_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' \
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>' \
        + "".join(paragraphs) + '<w:sectPr/></w:body></w:document>'
    content_types = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">' \
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>' \
        '<Default Extension="xml" ContentType="application/xml"/>' \
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>' \
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>' \
        '</Types>'
    rels = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' \
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>' \
        '</Relationships>'
    document_rels = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' \
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>' \
        '</Relationships>'
    styles = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' \
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">' \
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>' \
        '<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:sz w:val="36"/></w:rPr></w:style>' \
        '<w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:basedOn w:val="Normal"/><w:rPr><w:i/><w:sz w:val="24"/></w:rPr></w:style>' \
        '<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:sz w:val="28"/></w:rPr></w:style>' \
        '</w:styles>'
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, value in (
            ("[Content_Types].xml", content_types),
            ("_rels/.rels", rels),
            ("word/document.xml", document_xml),
            ("word/_rels/document.xml.rels", document_rels),
            ("word/styles.xml", styles),
        ):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            archive.writestr(info, value.encode("utf-8"))
    return output.getvalue()


def _pdf_escape(text: str) -> str:
    return text.encode("cp1252", errors="replace").decode("cp1252").replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def render_pdf(model: dict[str, Any]) -> bytes:
    """Render a portable text PDF using only standard-library PDF primitives."""
    document = model["document"]
    lines: list[str] = [document["title"]]
    if document.get("subtitle"):
        lines.append(document["subtitle"])
    lines.extend(["Authors: " + _authors(document), ""])
    for section in document["sections"]:
        lines.extend([section["heading"]])
        lines.extend(textwrap.wrap(section["body"], width=92) or [""])
        marker = f"[{section['content_class']} | {section['fidelity']}"
        if section.get("confidence") is not None:
            marker += f" | confidence={section['confidence']:.3f}"
        marker += "] sources=" + (", ".join(section["source_subject_ids"]) or "owner-authored")
        lines.extend(textwrap.wrap(marker, width=92) or [marker])
        lines.append("")
    lines.extend(["Provenance", *_provenance_lines(model)])
    pages = [lines[index:index + 48] for index in range(0, len(lines), 48)] or [[""]]
    page_numbers = [4 + index * 2 for index in range(len(pages))]
    objects: dict[int, bytes] = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: ("<< /Type /Pages /Count %d /Kids [%s] >>" % (len(pages), " ".join(f"{number} 0 R" for number in page_numbers))).encode("ascii"),
        3: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
    }
    for index, page_lines in enumerate(pages):
        page_number = page_numbers[index]
        content_number = page_number + 1
        commands = ["BT", "/F1 10 Tf", "50 742 Td", "13 TL"]
        for line in page_lines:
            commands.extend([f"({_pdf_escape(line)}) Tj", "T*"])
        commands.append("ET")
        stream = "\n".join(commands).encode("cp1252", errors="replace")
        objects[page_number] = f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents {content_number} 0 R >>".encode("ascii")
        objects[content_number] = f"<< /Length {len(stream)} >>\nstream\n".encode("ascii") + stream + b"\nendstream"
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0] * (max(objects) + 1)
    for number in sorted(objects):
        offsets[number] = len(output)
        output.extend(f"{number} 0 obj\n".encode("ascii"))
        output.extend(objects[number])
        output.extend(b"\nendobj\n")
    xref = len(output)
    output.extend(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii"))
    return bytes(output)


RENDERERS: dict[str, tuple[str, Callable[[dict[str, Any]], bytes]]] = {
    "markdown": ("md", render_markdown),
    "html": ("html", render_html),
    "pdf": ("pdf", render_pdf),
    "docx": ("docx", render_docx),
    "json": ("json", render_json),
}


def _validate_artifact(fmt: str, value: bytes, model: dict[str, Any]) -> None:
    title = model["document"]["title"]
    if not value:
        raise DocumentPipelineError(f"{fmt} artifact empty")
    if fmt == "markdown" and not value.startswith(("# " + title).encode("utf-8")):
        raise DocumentPipelineError("markdown title validation failed")
    if fmt == "html" and (b"<!doctype html>" not in value.lower() or html.escape(title).encode("utf-8") not in value):
        raise DocumentPipelineError("HTML validation failed")
    if fmt == "json":
        parsed = json.loads(value)
        if parsed.get("schema_version") != DOCUMENT_SCHEMA or parsed.get("source_binding") != model["source_binding"]:
            raise DocumentPipelineError("JSON reconstruction validation failed")
    if fmt == "pdf" and (not value.startswith(b"%PDF-1.4") or not value.rstrip().endswith(b"%%EOF") or b"/Type /Page " not in value):
        raise DocumentPipelineError("PDF validation failed")
    if fmt == "docx":
        with zipfile.ZipFile(io.BytesIO(value)) as archive:
            required = {"[Content_Types].xml", "_rels/.rels", "word/document.xml"}
            if not required.issubset(archive.namelist()) or html.escape(title).encode("utf-8") not in archive.read("word/document.xml"):
                raise DocumentPipelineError("DOCX validation failed")


def _write_immutable(path: Path, value: bytes) -> None:
    if path.exists() and path.read_bytes() != value:
        raise DocumentPipelineError(f"immutable artifact conflict: {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value)


def render_document_bundle(bundle: dict[str, Any], output_dir: Path, *, now: datetime | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    admission = validate_document_bundle(bundle, now=now)
    model = build_canonical_document(bundle)
    model_hash = sha256_uri(model)
    generation_id = hashlib.sha256((bundle["export_sha256"] + model_hash + RENDERER_VERSION).encode("utf-8")).hexdigest()[:24]
    document_id = bundle["document"]["document_id"]
    output_dir = Path(output_dir)
    artifacts = []
    for fmt in bundle["requested_formats"]:
        extension, renderer = RENDERERS[fmt]
        value = renderer(model)
        _validate_artifact(fmt, value, model)
        filename = f"{document_id}.{extension}"
        _write_immutable(output_dir / filename, value)
        artifacts.append({
            "format": fmt,
            "path": filename,
            "sha256": "sha256:" + sha256_hex_bytes(value),
            "bytes": len(value),
            "validation_state": "VALIDATED",
        })
    manifest = {
        "schema_version": MANIFEST_SCHEMA,
        "generation_id": generation_id,
        "document_id": document_id,
        "renderer_version": RENDERER_VERSION,
        "canonical_document_sha256": model_hash,
        "source_export_id": bundle["export_id"],
        "source_export_sha256": bundle["export_sha256"],
        "source_verification_root": bundle["source"]["verification_root"],
        "artifacts": artifacts,
        "validation_state": "VALIDATED",
        "publication_authorized": False,
        "release_authorized": False,
        "execution_authorized": False,
        "authority_effect": "NONE",
    }
    manifest["manifest_sha256"] = sha256_uri(manifest)
    receipt = {
        "schema_version": RECEIPT_SCHEMA,
        "receipt_type": "publisher.document_artifacts_rendered",
        "generation_id": generation_id,
        "document_id": document_id,
        "source_export_id": bundle["export_id"],
        "source_export_sha256": bundle["export_sha256"],
        "admission_receipt_sha256": admission["receipt_sha256"],
        "manifest_sha256": manifest["manifest_sha256"],
        "source_created_at": bundle["created_at"],
        "deterministic_time_basis": "source_bundle.created_at",
        "result": "GENERATED_VALIDATED_NOT_PUBLISHED",
        "publication_authorized": False,
        "release_authorized": False,
        "execution_authorized": False,
        "authority_effect": "NONE",
    }
    receipt["receipt_sha256"] = sha256_uri(receipt)
    _write_immutable(output_dir / "artifact-manifest.json", (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    _write_immutable(output_dir / "rendering-receipt.json", (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    verify_artifact_manifest(output_dir, manifest)
    return manifest, receipt


def verify_artifact_manifest(output_dir: Path, manifest: dict[str, Any]) -> bool:
    unhashed = copy.deepcopy(manifest)
    stored_manifest_hash = unhashed.pop("manifest_sha256", None)
    if stored_manifest_hash != sha256_uri(unhashed):
        return False
    for artifact in manifest.get("artifacts", []):
        path = Path(output_dir) / artifact["path"]
        if not path.is_file():
            return False
        value = path.read_bytes()
        if len(value) != artifact["bytes"] or "sha256:" + sha256_hex_bytes(value) != artifact["sha256"]:
            return False
    return True
