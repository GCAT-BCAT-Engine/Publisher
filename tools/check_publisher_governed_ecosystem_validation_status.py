from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "PUBLISHER_GOVERNED_ECOSYSTEM_VALIDATION_STATUS.md"
EVIDENCE = ROOT / "docs" / "PUBLISHER_GOVERNED_ECOSYSTEM_WORKFLOW_EVIDENCE.md"

REQUIRED = [
    "PUBLISHER_GOVERNED_ECOSYSTEM_VALIDATION_STATUS_PRESENT",
    "VALIDATION_CHECKERS_INSTALLED",
    "DEDICATED_VALIDATION_WORKFLOW_PRESENT",
    "WORKFLOW_EVIDENCE_RECORDED",
    "DOWNSTREAM_PROPAGATION_FORMALLY_DEFERRED",
    "tools/check_governed_ecosystem_site_mirror_awareness.py",
    "tools/check_stegguardian_propagation_status.py",
    "tools/check_publisher_governed_ecosystem_sync_status.py",
    "tools/check_publisher_governed_ecosystem_validation_status.py",
    "tools/check_publisher_governed_ecosystem_workflow_request.py",
    "github/workflows/validate-emergency-ai-cases.yml",
    "github/workflows/validate-governed-ecosystem-awareness.yml",
    "docs/PUBLISHER_GOVERNED_ECOSYSTEM_WORKFLOW_EVIDENCE.md",
]


def main():
    errors = []
    if not DOC.exists():
        errors.append("missing_validation_status_doc")
        text = ""
    else:
        text = DOC.read_text(encoding="utf-8")
    if not EVIDENCE.exists():
        errors.append("missing_workflow_evidence_doc")
    for item in REQUIRED:
        if item not in text:
            errors.append("missing:" + item)
    if errors:
        print("PUBLISHER GOVERNED ECOSYSTEM VALIDATION STATUS: FAIL - " + ", ".join(errors))
        return 1
    print("PUBLISHER GOVERNED ECOSYSTEM VALIDATION STATUS: PASS - workflow evidence recorded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
