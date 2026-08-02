#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers" / "development-without-domination"
MANIFEST = PAPER / "publication-manifest.json"
STATUS = PAPER / "publication-status.json"
RECEIPT = PAPER / "publication-receipt.json"
PDF = PAPER / "Development_Without_Domination_Rigel_Randolph_Final.pdf"
DOCX = PAPER / "Development_Without_Domination_Rigel_Randolph_Final.docx"
EXPECTED_PDF_SHA = "c2fcb0ce76f5eaba1a6dd4ccdd358fcae29b32b3110767b5f2b5b2ffa347c29d"
EXPECTED_PDF_BYTES = 149969
EXPECTED_DOCX_SHA = "fa7d9c2069ce17e26f1c7f5f4a6bb983ccd4229c11ebc1fd8c788b8d7d2fc2ab"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def artifact(path: Path, expected_sha: str, expected_bytes: int | None = None) -> dict:
    present = path.is_file()
    observed_sha = digest(path) if present else None
    observed_bytes = path.stat().st_size if present else None
    hash_ok = observed_sha == expected_sha
    size_ok = expected_bytes is None or observed_bytes == expected_bytes
    return {
        "path": str(path.relative_to(ROOT)),
        "present": present,
        "observed_sha256": observed_sha,
        "expected_sha256": expected_sha,
        "observed_bytes": observed_bytes,
        "expected_bytes": expected_bytes,
        "verified": bool(present and hash_ok and size_ok),
    }


def main() -> int:
    manifest = json.loads(MANIFEST.read_text())
    prior = json.loads(STATUS.read_text()) if STATUS.exists() else {}

    pdf = artifact(PDF, EXPECTED_PDF_SHA, EXPECTED_PDF_BYTES)
    docx = artifact(DOCX, EXPECTED_DOCX_SHA)
    site_receipt = PAPER / "site-mirror-receipt.json"
    site_ready = site_receipt.is_file()

    if not pdf["present"] or not docx["present"]:
        state = "BLOCKED"
        reason = "EXACT_ARTIFACTS_NOT_REPOSITORY_RESIDENT"
    elif not pdf["verified"] or not docx["verified"]:
        state = "FAILED"
        reason = "ARTIFACT_IDENTITY_MISMATCH"
    elif not site_ready:
        state = "RETRY"
        reason = "WAITING_FOR_VERIFIED_SITE_PROPAGATION"
    else:
        state = "REVIEW_REQUIRED"
        reason = "ARTIFACTS_AND_SITE_RECEIPT_PRESENT_REVIEW_AUTHORITY_REQUIRED"

    next_task = {
        "repository": "GCAT-BCAT-Engine/Publisher",
        "path": pdf["path"] if not pdf["verified"] else docx["path"] if not docx["verified"] else str(site_receipt.relative_to(ROOT)),
        "action": (
            "Install exact PDF bytes matching the declared hash and byte count."
            if not pdf["verified"]
            else "Install exact DOCX bytes matching the declared hash."
            if not docx["verified"]
            else "Acquire and validate the committed Site mirror receipt."
        ),
    }

    status = {
        **prior,
        "schema_version": "1.1.0",
        "goal_id": "PUBLISHER-0001-DWD-PUBLICATION",
        "repository": "GCAT-BCAT-Engine/Publisher",
        "branch": manifest.get("branch"),
        "state": state,
        "reason": reason,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "artifact_checks": {"pdf": pdf, "docx": docx},
        "site_propagation": {
            "receipt_path": str(site_receipt.relative_to(ROOT)),
            "state": "COMPLETE" if site_ready else "BLOCKED",
            "release_condition": "Site commits a receipt binding exact PDF identity to a directly verified deployed route.",
        },
        "authority": {
            "publication": False,
            "release": False,
            "site_mirror": False,
            "wiki_projection": False,
            "admissibility": False,
        },
        "next_executable_task": next_task,
        "external_tasks": [],
    }
    STATUS.write_text(json.dumps(status, indent=2) + "\n")

    if state == "REVIEW_REQUIRED":
        RECEIPT.write_text(json.dumps({
            "schema_version": "1.0.0",
            "goal_id": status["goal_id"],
            "state": "REVIEW_REQUIRED",
            "pdf_sha256": pdf["observed_sha256"],
            "pdf_bytes": pdf["observed_bytes"],
            "docx_sha256": docx["observed_sha256"],
            "site_receipt_present": site_ready,
            "publication_authority": False,
            "generated_at": status["observed_at"],
        }, indent=2) + "\n")
    elif RECEIPT.exists():
        RECEIPT.unlink()

    print(json.dumps({"state": state, "reason": reason, "next_executable_task": next_task}, indent=2))
    return 0 if state in {"BLOCKED", "RETRY", "REVIEW_REQUIRED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
