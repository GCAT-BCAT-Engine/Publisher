from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "PUBLISHER_GOVERNED_ECOSYSTEM_SYNC_STATUS.md"

REQUIRED = [
    "PUBLISHER_GOVERNED_ECOSYSTEM_SYNC_STATUS_PRESENT",
    "VALIDATION_DOC_UPDATED",
    "AWARENESS_CHECKER_WIRED",
    "DOWNSTREAM_DESTINATION_PENDING",
    "StegVerse-Labs/admissibility-wiki",
    "StegVerse-Labs/Site",
    "GCAT-BCAT-Engine/Publisher",
]


def main():
    errors = []
    if not DOC.exists():
        errors.append("missing_sync_status_doc")
        text = ""
    else:
        text = DOC.read_text(encoding="utf-8")
    for item in REQUIRED:
        if item not in text:
            errors.append("missing:" + item)
    if errors:
        print("PUBLISHER GOVERNED ECOSYSTEM SYNC STATUS: FAIL - " + ", ".join(errors))
        return 1
    print("PUBLISHER GOVERNED ECOSYSTEM SYNC STATUS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
