from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "STEGGUARDIAN_PROPAGATION_STATUS.md"

REQUIRED = [
    "STEGGUARDIAN_PROPAGATION_PENDING_DESTINATION_NOT_FOUND",
    "stegguardian-wiki",
    "record_pending_downstream_propagation_only",
]


def main():
    errors = []
    if not DOC.exists():
        errors.append("missing_status_doc")
        text = ""
    else:
        text = DOC.read_text(encoding="utf-8")
    for item in REQUIRED:
        if item not in text:
            errors.append("missing:" + item)
    if errors:
        print("STEGGUARDIAN PROPAGATION STATUS: FAIL - " + ", ".join(errors))
        return 1
    print("STEGGUARDIAN PROPAGATION STATUS: PASS - destination pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
