#!/usr/bin/env python3
"""Build and validate the canonical LinkedIn PDF for SV-COST five-lane results."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "papers/five-lane-reconstructable-governance-publication-manifest.json"
OUT_DIR = ROOT / "artifacts/five-lane-reconstructable-governance"
PDF_PATH = OUT_DIR / "StegVerse_Five_Lane_Cost_Results_LinkedIn.pdf"
RECEIPT_PATH = OUT_DIR / "pdf-validation-receipt.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def money(value: float) -> str:
    return f"${value:.12f}" if value < 0.000001 else f"${value:.6f}"


def paragraph(text: str, style):
    return Paragraph(text.replace("&", "&amp;"), style)


def main() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    lanes = manifest["lanes"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="SVTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=23,
        leading=27,
        textColor=colors.HexColor("#102A43"),
        alignment=TA_CENTER,
        spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name="SVSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1E6F93"),
        alignment=TA_CENTER,
        spaceAfter=18,
    ))
    styles.add(ParagraphStyle(
        name="SVHeading",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=19,
        textColor=colors.HexColor("#102A43"),
        spaceBefore=6,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="SVBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="SVSmall",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#566573"),
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="SVCallout",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#102A43"),
        leftIndent=12,
        rightIndent=12,
        spaceBefore=8,
        spaceAfter=8,
        borderColor=colors.HexColor("#2C9BC5"),
        borderWidth=1,
        borderPadding=9,
        backColor=colors.HexColor("#EEF7FA"),
    ))

    story = []
    story.append(paragraph("FIVE-LANE COST RESULTS FOR RECONSTRUCTABLE GOVERNANCE", styles["SVTitle"]))
    story.append(paragraph(
        "Observed execution, normalized admissibility, and bounded economic interpretation",
        styles["SVSubtitle"],
    ))
    meta = [
        ["Experiment", manifest["experiment_id"]],
        ["Task", manifest["task_id"]],
        ["Operation class", manifest["operation_class"]],
        ["Comparison unit", manifest["comparison_unit"]],
        ["Publication status", manifest["publication_status"]],
    ]
    mt = Table(meta, colWidths=[1.45 * inch, 5.45 * inch])
    mt.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#9FB3C8")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F0F5")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.extend([mt, Spacer(1, 12)])
    story.append(paragraph(
        "All five lanes completed successfully, preserved task identity, produced the same normalized admissible outcome, and passed the publication gate.",
        styles["SVCallout"],
    ))
    story.append(paragraph("Headline result", styles["SVHeading"]))
    story.append(paragraph(
        "For this bounded reconstruction task, StegVerse-only deterministic reconstruction was the lowest-cost successful equivalent admissible lane. OpenAI governance was approximately cost-neutral (+0.073%), while Anthropic governance was 33.22% lower than Anthropic raw in this observed run.",
        styles["SVBody"],
    ))
    result_rows = [["Lane", "Cost / admissible outcome", "Latency", "Result"]]
    for lane in lanes:
        result_rows.append([
            lane["lane"], money(lane["cost_usd"]), f"{lane['latency_seconds']:.9f} s", lane["status"]
        ])
    rt = Table(result_rows, colWidths=[2.85 * inch, 1.75 * inch, 1.35 * inch, 0.75 * inch], repeatRows=1)
    rt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#102A43")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#9FB3C8")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F7F9")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.extend([rt, Spacer(1, 8)])
    story.append(paragraph(
        "Provider costs are reconstructed from retained token-usage receipts using a versioned declared price card and are not invoice-reconciled charges. The StegVerse figure combines measured runtime and output size with declared runner and storage rates.",
        styles["SVSmall"],
    ))

    story.append(PageBreak())
    story.append(paragraph("1. Research question and task contract", styles["SVHeading"]))
    story.append(paragraph(
        "Can OpenAI raw, OpenAI governed, Anthropic raw, Anthropic governed, and StegVerse-only deterministic reconstruction produce the same successful equivalent admissible outcome under one task contract, and what is the declared-rate cost of each lane?",
        styles["SVBody"],
    ))
    story.append(paragraph(
        "The task began with balance 100, risk score 1, and active standing. Six ordered events were evaluated. Credits increase balance; debits are denied when they cross minimum balance or standing is not active; risk additions are denied when they exceed the maximum risk score; denied events never mutate state.",
        styles["SVBody"],
    ))
    task_rows = [
        ["Event", "Operation", "Amount", "Required decision"],
        ["E01", "Credit", "25", "ALLOW - CREDIT_APPLIED"],
        ["E02", "Debit", "40", "ALLOW - DEBIT_WITHIN_BOUNDARY"],
        ["E03", "Risk add", "2", "ALLOW - RISK_WITHIN_BOUNDARY"],
        ["E04", "Debit", "100", "DENY - MINIMUM_BALANCE_VIOLATION"],
        ["E05", "Risk add", "3", "DENY - MAXIMUM_RISK_VIOLATION"],
        ["E06", "Debit", "10", "ALLOW - DEBIT_WITHIN_BOUNDARY"],
    ]
    tt = Table(task_rows, colWidths=[0.7 * inch, 1.05 * inch, 0.75 * inch, 4.2 * inch], repeatRows=1)
    tt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#102A43")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#9FB3C8")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F7F9")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.extend([tt, Spacer(1, 8)])
    story.append(paragraph(
        "Required final state: balance 75; risk score 3; standing active; applied events 4; denied events 2.",
        styles["SVCallout"],
    ))
    story.append(paragraph("2. Admissibility and normalization", styles["SVHeading"]))
    story.append(paragraph(
        "Provider outputs were not admitted merely because they were valid JSON or semantically plausible. Each output was normalized into the same contract and compared against task identity, final state, ordered event decisions, applied count, denied count, and claim boundary. Missing, contradictory, unsupported, or incorrect transitions failed closed. All five passing lanes produced the same normalized outcome hash.",
        styles["SVBody"],
    ))
    story.append(paragraph(manifest["normalized_outcome_hash"], styles["SVSmall"]))

    story.append(PageBreak())
    story.append(paragraph("3. How the cost numbers were generated", styles["SVHeading"]))
    story.append(paragraph(
        "Provider cost = (input tokens x input rate + output tokens x output rate) / 1,000,000.",
        styles["SVCallout"],
    ))
    story.append(paragraph(
        "Declared rates: OpenAI input $5.00 per million and output $30.00 per million; Anthropic input $3.00 per million and output $15.00 per million.",
        styles["SVBody"],
    ))
    story.append(paragraph(
        "StegVerse local cost = runtime seconds x ($0.008 / 60) + output GB x $0.008.",
        styles["SVCallout"],
    ))
    story.append(paragraph(
        "Measured StegVerse-only runtime was approximately 0.000000461 seconds and normalized output size was 353 bytes. The modeled compute component was approximately $0.000000000061 and storage component approximately $0.000000002824, for a total of $0.000000002885.",
        styles["SVBody"],
    ))
    story.append(paragraph("4. Provider-pair findings", styles["SVHeading"]))
    pair_rows = [
        ["Provider", "Raw", "Governed", "Delta", "Observed delta"],
        ["OpenAI", "$0.006875", "$0.006880", "+$0.000005", "+0.072727%"],
        ["Anthropic", "$0.010656", "$0.007116", "-$0.003540", "-33.220721%"],
    ]
    pt = Table(pair_rows, colWidths=[1.25 * inch, 1.25 * inch, 1.25 * inch, 1.25 * inch, 1.35 * inch], repeatRows=1)
    pt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#102A43")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#9FB3C8")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F7F9")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.extend([pt, Spacer(1, 8)])
    story.append(paragraph(
        "OpenAI governance was effectively cost-neutral in this run. Anthropic governance used fewer output tokens and was 33.22% lower than Anthropic raw while producing the same normalized admissible outcome. This is a single-run observation, not a guaranteed provider effect.",
        styles["SVBody"],
    ))

    story.append(PageBreak())
    story.append(paragraph("5. Bounded reconstruction comparison", styles["SVHeading"]))
    story.append(paragraph(
        "StegVerse-only did not perform fresh open-ended model inference. It deterministically reconstructed an already-defined admissible successor state from the task contract. Because all five lanes produced the same normalized admissible result for this operation, a matched-operation comparison is valid here.",
        styles["SVBody"],
    ))
    story.append(paragraph(
        "Provider-to-StegVerse cost ratios ranged from approximately 2.38 million to 3.69 million times, with matched-operation modeled reductions above 99.99995% for this bounded deterministic reconstruction.",
        styles["SVBody"],
    ))
    story.append(paragraph(
        "These very large ratios must not be generalized to discovery, open-ended reasoning, fresh inference, all enterprise workloads, or company-wide ROI. They identify where deterministic reconstruction can avoid unnecessary new generation; they do not establish that deterministic reconstruction replaces frontier-model capability.",
        styles["SVCallout"],
    ))
    story.append(paragraph("6. What the result establishes", styles["SVHeading"]))
    for item in [
        "A provider-neutral five-lane harness can enforce admissibility before cost selection.",
        "All five lanes can produce the same normalized governed-state result under one contract.",
        "Provider-call governance overhead can be close to zero or negative depending on output behavior.",
        "Deterministic reconstruction can be materially cheaper when reconstruction is the correct operation.",
        "Cost should be reported per successful equivalent admissible outcome, not merely per attempt or token count.",
    ]:
        story.append(paragraph("- " + item, styles["SVBody"]))
    story.append(paragraph("7. What the result does not establish", styles["SVHeading"]))
    for item in [
        "Replacement of foundation models for fresh reasoning or discovery.",
        "Universal savings across providers, workloads, or organizations.",
        "Invoice-reconciled provider charges or fully burdened enterprise cost.",
        "Company-wide ROI or fresh-inference equivalence.",
    ]:
        story.append(paragraph("- " + item, styles["SVBody"]))

    story.append(PageBreak())
    story.append(paragraph("8. Conclusion and evidence", styles["SVHeading"]))
    story.append(paragraph(
        "The five-lane experiment completed with all lanes successful, equivalent, and admissible. StegVerse-only deterministic reconstruction was the lowest-cost admissible lane for this bounded operation. The evidence supports a narrow conclusion: reconstructable governance can be technically available, provider-neutral, admissibility-preserving, and economically negligible or advantageous for bounded state reconstruction.",
        styles["SVBody"],
    ))
    story.append(paragraph(
        "Broader provider-profit, enterprise ROI, and fresh-inference claims require separate held-out tasks, repeated trials, invoice reconciliation, and fully burdened operating-cost analysis.",
        styles["SVCallout"],
    ))
    evidence = [
        ["Evidence repository", "GCAT-BCAT-Engine/workflows"],
        ["Evidence commit", manifest["canonical_sources"]["result_commit"]],
        ["Publisher source", manifest["canonical_sources"]["paper_path"]],
        ["Site source", manifest["canonical_sources"]["site_path"]],
        ["Task-contract hash", manifest["task_contract_hash"]],
        ["Outcome hash", manifest["normalized_outcome_hash"]],
        ["Price-card status", manifest["price_card_status"]],
    ]
    et = Table(evidence, colWidths=[1.45 * inch, 5.35 * inch])
    et.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#9FB3C8")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F0F5")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.extend([et, Spacer(1, 12)])
    story.append(paragraph(
        "Public paper: https://stegverse.org/papers/sv-cost-relational-analysis.html",
        styles["SVSmall"],
    ))
    story.append(paragraph("Author: Rigel Randolph | Organization: StegVerse | License: CC-BY-4.0", styles["SVSmall"]))

    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=LETTER,
        leftMargin=0.62 * inch,
        rightMargin=0.62 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
        title="Five-Lane Cost Results for Reconstructable Governance",
        author="Rigel Randolph / StegVerse",
        subject="Bounded five-lane reconstructable governance cost results",
    )
    doc.build(story)

    data = PDF_PATH.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    reader = PdfReader(str(PDF_PATH))
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    required_markers = [
        "FIVE-LANE COST RESULTS FOR RECONSTRUCTABLE GOVERNANCE",
        "OpenAI raw",
        "$0.006875",
        "OpenAI governed",
        "$0.006880",
        "Anthropic raw",
        "$0.010656",
        "Anthropic governed",
        "$0.007116",
        "StegVerse-only",
        "$0.000000002885",
        "universal provider economics",
        "company-wide ROI",
        "fresh-inference equivalence",
    ]
    checks = {marker: marker in extracted for marker in required_markers}
    complete = all(checks.values()) and len(reader.pages) >= 4 and len(data) > 10000
    receipt = {
        "schema_version": "1.0.0",
        "publication_id": manifest["publication_id"],
        "generated_at": utc_now(),
        "pdf_path": str(PDF_PATH.relative_to(ROOT)),
        "sha256": "sha256:" + sha,
        "bytes": len(data),
        "pages": len(reader.pages),
        "required_marker_checks": checks,
        "all_required_markers_present": all(checks.values()),
        "validation_state": "COMPLETE" if complete else "FAILED",
        "claim_boundary": manifest["claim_boundary"],
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    manifest["artifact_state"] = "COMPLETE" if complete else "FAILED"
    manifest["linkedin_pdf"].update({
        "sha256": receipt["sha256"],
        "bytes": receipt["bytes"],
        "pages": receipt["pages"],
    })
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
