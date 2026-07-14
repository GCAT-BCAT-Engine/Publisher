#!/usr/bin/env python3
"""Validate GCAT capacity bibliography keys and claim-boundary records."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Set

ROOT = Path(__file__).resolve().parents[1]
BIB = ROOT / "papers" / "GCAT-BCAT" / "references" / "gcat_capacity_primary_sources.bib"
RELATED = ROOT / "papers" / "GCAT-BCAT" / "sections" / "P14_related_work_v1.md"
REVIEW = ROOT / "docs" / "gcat-capacity-source-review.md"

REQUIRED_KEYS = {
    "ames2017cbfqp",
    "ames2019cbfsurvey",
    "xu2018robustcbf",
    "aubin1991viability",
    "aubin2011viability",
    "cobb1928production",
    "arrow1961ces",
    "simon1955behavioral",
    "vaughan1999darkside",
    "vaughan1996challenger",
    "leveson2011safer",
}

REQUIRED_BOUNDARY_PHRASES = {
    "does not validate GCAT empirically",
    "does not compute the GCAT viability kernel",
    "must not be used to equate the GCAT observational case with Challenger",
    "Bibliographic metadata must be checked against publisher or DOI records before release",
}


def fail(message: str, failures: List[str]) -> None:
    failures.append(message)


def bib_keys(text: str) -> Set[str]:
    return set(re.findall(r"@\w+\{([^,\s]+)", text))


def citation_keys(text: str) -> Set[str]:
    return set(re.findall(r"@([A-Za-z0-9_:-]+)", text))


def main() -> int:
    failures: List[str] = []
    for path in (BIB, RELATED, REVIEW):
        if not path.is_file():
            fail(f"missing required file: {path.relative_to(ROOT)}", failures)

    if failures:
        print("GCAT bibliography validation: FAIL")
        for item in failures:
            print(f"- {item}")
        return 1

    bib_text = BIB.read_text(encoding="utf-8")
    related_text = RELATED.read_text(encoding="utf-8")
    review_text = REVIEW.read_text(encoding="utf-8")

    keys = bib_keys(bib_text)
    cited = citation_keys(related_text)

    missing_bib = REQUIRED_KEYS - keys
    if missing_bib:
        fail(f"missing bibliography keys: {sorted(missing_bib)}", failures)

    undefined = cited - keys
    if undefined:
        fail(f"undefined citation keys: {sorted(undefined)}", failures)

    uncited = REQUIRED_KEYS - cited
    if uncited:
        fail(f"required primary sources not cited in related work: {sorted(uncited)}", failures)

    duplicate_count = len(re.findall(r"@\w+\{", bib_text)) - len(keys)
    if duplicate_count:
        fail("duplicate bibliography keys detected", failures)

    for key in REQUIRED_KEYS:
        if f"`{key}`" not in review_text:
            fail(f"source-review matrix missing key: {key}", failures)

    for phrase in REQUIRED_BOUNDARY_PHRASES:
        if phrase not in review_text:
            fail(f"source-review boundary missing: {phrase}", failures)

    for marker in ("Control barrier functions", "Viability", "Production functions", "organizational failure"):
        if marker.lower() not in related_text.lower():
            fail(f"related-work topic missing: {marker}", failures)

    if "GCAT does not claim a new general barrier theorem" not in related_text:
        fail("barrier-theory claim boundary missing", failures)
    if "do not compute a viability kernel" not in related_text:
        fail("viability claim boundary missing", failures)
    if "not evidence for the paper's federal IT observation" not in related_text:
        fail("organizational-case claim boundary missing", failures)

    if failures:
        print("GCAT bibliography validation: FAIL")
        for item in failures:
            print(f"- {item}")
        return 1

    print("GCAT bibliography validation: PASS")
    print(f"- bibliography entries: {len(keys)}")
    print(f"- cited primary sources: {len(cited)}")
    print("- source-to-claim matrix: present")
    print("- release metadata verification: still required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
