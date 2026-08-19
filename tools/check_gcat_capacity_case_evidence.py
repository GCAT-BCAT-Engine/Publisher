#!/usr/bin/env python3
"""Validate GCAT case-study provenance and bounded claim language."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]
NOTE = ROOT / "docs/gcat-capacity-case-evidence-note.md"
SECTION = ROOT / "papers/GCAT-BCAT/sections/P14_case_study_v1.md"

REQUIRED_SECTION_PHRASES = (
    "author's first-person operational recollection",
    "not as a calibrated dataset",
    "does not establish the mismatch as an independently verified root cause",
    "not a complete incident census",
    "not a claim of forensic impossibility",
    "No numerical `Omega`, elasticity, calibration, viability-kernel result, malicious activity, wrongdoing, or causal mechanism is claimed",
)

REQUIRED_NOTE_MARKERS = (
    "QUALIFIED",
    "EXCLUDED",
    "first-person quantitative recollection",
    "unsupported allegation",
    "unsupported scale claim",
    "Issue #6 evidence-review lane",
)

PROHIBITED_SECTION_PHRASES = (
    "more than 10,000 devices",
    "criminal activity",
    "coordinated activity",
    "proved overload",
    "Omega > 1 occurred",
)


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def main() -> int:
    failures: List[str] = []
    for path in (NOTE, SECTION):
        if not path.is_file():
            failures.append(f"missing required file: {path.relative_to(ROOT)}")

    if failures:
        print("GCAT case evidence validation: FAIL")
        for item in failures:
            print(f"- {item}")
        return 1

    note = NOTE.read_text(encoding="utf-8")
    section = SECTION.read_text(encoding="utf-8")
    section_norm = normalized(section)

    for phrase in REQUIRED_SECTION_PHRASES:
        if normalized(phrase) not in section_norm:
            failures.append(f"case section boundary missing: {phrase}")

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note:
            failures.append(f"case evidence note marker missing: {marker}")

    for phrase in PROHIBITED_SECTION_PHRASES:
        if normalized(phrase) in section_norm:
            failures.append(f"prohibited case claim present: {phrase}")

    for variable in ("`g`", "`c`", "`t`", "`a`"):
        if variable not in section:
            failures.append(f"case mapping missing variable: {variable}")

    if failures:
        print("GCAT case evidence validation: FAIL")
        for item in failures:
            print(f"- {item}")
        return 1

    print("GCAT case evidence validation: PASS")
    print("- provenance: first-person and bounded")
    print("- excluded claims: preserved")
    print("- qualitative GCAT mapping: present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
