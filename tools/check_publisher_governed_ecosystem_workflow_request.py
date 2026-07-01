from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "PUBLISHER_GOVERNED_ECOSYSTEM_WORKFLOW_EVIDENCE_REQUEST.md"

REQUIRED = [
    "PUBLISHER_GOVERNED_ECOSYSTEM_WORKFLOW_EVIDENCE_REQUEST_PRESENT",
    "WORKFLOW_RUN_PENDING",
    "github/workflows/validate-emergency-ai-cases.yml",
    "python tools/check_publisher_activation.py",
]


def main():
    errors = []
    if not DOC.exists():
        errors.append("missing_workflow_request")
        text = ""
    else:
        text = DOC.read_text(encoding="utf-8")
    for item in REQUIRED:
        if item not in text:
            errors.append("missing:" + item)
    if errors:
        print("PUBLISHER GOVERNED ECOSYSTEM WORKFLOW REQUEST: FAIL - " + ", ".join(errors))
        return 1
    print("PUBLISHER GOVERNED ECOSYSTEM WORKFLOW REQUEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
