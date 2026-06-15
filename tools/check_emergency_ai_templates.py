#!/usr/bin/env python3
"""Check emergency AI restriction templates for scaffold consistency."""

from __future__ import annotations

from pathlib import Path

TEMPLATE_PATHS = [
    Path("templates/emergency-ai-restriction.public-case.template.md"),
    Path("templates/emergency-ai-restriction.case.template.json"),
    Path("templates/emergency-ai-restriction.sources.template.json"),
    Path("templates/emergency-ai-restriction.receipt.template.json"),
]

REQUIRED_SHARED_PLACEHOLDERS = [
    "CASE-YYYY-MM-SLUG",
    "Emergency AI Restriction Case Title",
]

DATE_PLACEHOLDERS = [
    "EVENT-YYYY-MM-DD",
    "OBSERVED-YYYY-MM-DD",
]

FORBIDDEN_PLACEHOLDERS = [
    "\"YYYY-MM-DD\"",
    ": YYYY-MM-DD",
]

EXPECTED_OUTPUT_PATHS = [
    "cases/CASE-YYYY-MM-SLUG.md",
    "governance/cases/CASE-YYYY-MM-SLUG.case.json",
    "governance/cases/CASE-YYYY-MM-SLUG.sources.json",
    "governance/receipts/CASE-YYYY-MM-SLUG.receipt.json",
]


def fail(message: str) -> int:
    print(f"template check failed: {message}")
    return 1


def main() -> int:
    for path in TEMPLATE_PATHS:
        if not path.exists():
            return fail(f"missing template: {path}")

        text = path.read_text(encoding="utf-8")

        if "CASE-YYYY-MM-SLUG" not in text:
            return fail(f"missing case placeholder in {path}")

        for forbidden in FORBIDDEN_PLACEHOLDERS:
            if forbidden in text:
                return fail(f"ambiguous date placeholder {forbidden!r} found in {path}")

        if path.suffix == ".json":
            if path.name.endswith("case.template.json") or path.name.endswith("receipt.template.json"):
                for placeholder in DATE_PLACEHOLDERS:
                    if placeholder not in text:
                        return fail(f"missing {placeholder} in {path}")
            if path.name.endswith("sources.template.json") and "OBSERVED-YYYY-MM-DD" not in text:
                return fail(f"missing OBSERVED-YYYY-MM-DD in {path}")

    public_case_text = TEMPLATE_PATHS[0].read_text(encoding="utf-8")
    for output_path in EXPECTED_OUTPUT_PATHS[1:]:
        if output_path not in public_case_text:
            return fail(f"public case template missing linked path: {output_path}")

    scaffold_text = Path("tools/create_emergency_ai_case_scaffold.py").read_text(encoding="utf-8")
    for output_path in EXPECTED_OUTPUT_PATHS:
        if output_path.replace("CASE-YYYY-MM-SLUG", "{case_id}") not in scaffold_text:
            return fail(f"scaffold generator missing output path: {output_path}")

    print("valid: emergency AI templates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
