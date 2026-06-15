#!/usr/bin/env python3
"""Create a four-file emergency AI restriction case scaffold from templates."""

from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATE_MAP = {
    "templates/emergency-ai-restriction.public-case.template.md": "cases/{case_id}.md",
    "templates/emergency-ai-restriction.case.template.json": "governance/cases/{case_id}.case.json",
    "templates/emergency-ai-restriction.sources.template.json": "governance/cases/{case_id}.sources.json",
    "templates/emergency-ai-restriction.receipt.template.json": "governance/receipts/{case_id}.receipt.json",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a Publisher emergency AI restriction case scaffold."
    )
    parser.add_argument("case_id", help="Case ID, for example CASE-2026-06-EXAMPLE")
    parser.add_argument("--title", default="Emergency AI Restriction Case Title")
    parser.add_argument("--event-date", default="EVENT-YYYY-MM-DD")
    parser.add_argument("--observed-date", default="OBSERVED-YYYY-MM-DD")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing scaffold files. By default existing files are preserved.",
    )
    return parser.parse_args()


def render_template(text: str, args: argparse.Namespace) -> str:
    return (
        text.replace("CASE-YYYY-MM-SLUG", args.case_id)
        .replace("Emergency AI Restriction Case Title", args.title)
        .replace("EVENT-YYYY-MM-DD", args.event_date)
        .replace("OBSERVED-YYYY-MM-DD", args.observed_date)
    )


def main() -> int:
    args = parse_args()
    created: list[str] = []
    skipped: list[str] = []

    for template_path_text, output_path_template in TEMPLATE_MAP.items():
        template_path = Path(template_path_text)
        output_path = Path(output_path_template.format(case_id=args.case_id))

        if not template_path.exists():
            print(f"missing template: {template_path}")
            return 1

        if output_path.exists() and not args.force:
            skipped.append(str(output_path))
            continue

        output_path.parent.mkdir(parents=True, exist_ok=True)
        rendered = render_template(template_path.read_text(encoding="utf-8"), args)
        output_path.write_text(rendered, encoding="utf-8")
        created.append(str(output_path))

    for path in created:
        print(f"created: {path}")
    for path in skipped:
        print(f"skipped existing: {path}")

    if not created and skipped:
        print("no files created; use --force to overwrite existing scaffold files")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
