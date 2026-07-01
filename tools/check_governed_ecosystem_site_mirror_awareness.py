from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "GOVERNED_ECOSYSTEM_SITE_MIRROR_AWARENESS.md"

REQUIRED = [
    "PUBLISHER_GOVERNED_ECOSYSTEM_SITE_MIRROR_AWARENESS_PRESENT",
    "StegVerse-Labs/admissibility-wiki",
    "StegVerse-Labs/Site/governed-ecosystem.html",
    "publication_awareness_only",
]


def main():
    errors = []
    if not DOC.exists():
        errors.append("missing_awareness_doc")
        text = ""
    else:
        text = DOC.read_text(encoding="utf-8")
    for item in REQUIRED:
        if item not in text:
            errors.append("missing:" + item)
    if errors:
        print("PUBLISHER GOVERNED ECOSYSTEM SITE MIRROR AWARENESS: FAIL - " + ", ".join(errors))
        return 1
    print("PUBLISHER GOVERNED ECOSYSTEM SITE MIRROR AWARENESS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
