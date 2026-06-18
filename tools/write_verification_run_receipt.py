#!/usr/bin/env python3
"""Write Publisher-to-Site verification run receipts from workflow context.

This script is intentionally workflow-friendly: it does not require a human to
copy values from the Actions UI into a receipt template. Values are read from
explicit environment variables and written as a JSON receipt that can be uploaded
as a workflow artifact or committed by a later governed receipt step.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "verification-runs"


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def env_bool(name: str, default: bool = False) -> bool:
    value = env(name)
    if not value:
        return default
    return value.lower() in {"1", "true", "yes", "y", "on"}


def safe_name(value: str) -> str:
    allowed = []
    for char in value:
        if char.isalnum() or char in {"-", "_", "."}:
            allowed.append(char)
        else:
            allowed.append("-")
    return "".join(allowed).strip("-") or "unknown"


def build_receipt() -> dict:
    dry_run = env_bool("DRY_RUN", default=False)
    run_id = env("GITHUB_RUN_ID", "unknown")
    run_attempt = env("GITHUB_RUN_ATTEMPT", "1")
    server_url = env("GITHUB_SERVER_URL", "https://github.com")
    repository = env("GITHUB_REPOSITORY", "GCAT-BCAT-Engine/Publisher")

    github_run_url = f"{server_url}/{repository}/actions/runs/{run_id}"
    site_dispatch_attempted = not dry_run and env_bool("SITE_DISPATCH_ATTEMPTED", default=False)

    return {
        "receipt_type": "publisher_to_site_verification_run",
        "status": env("RECEIPT_STATUS", "generated"),
        "run_class": "dry_run" if dry_run else "live_dispatch",
        "publisher_repository": repository,
        "site_repository": env("SITE_REPOSITORY", "StegVerse-Labs/Site"),
        "publisher_workflow": ".github/workflows/dispatch-site-mirror.yml",
        "publisher_activation_runner": "tools/check_publisher_activation.py",
        "site_workflow": "StegVerse-Labs/Site/.github/workflows/mirror-papers.yml",
        "source_repository": env("SOURCE_REPOSITORY", "GCAT-BCAT-Engine/Publisher"),
        "source_ref": env("SOURCE_REF", "main"),
        "dry_run": dry_run,
        "github_run_url": github_run_url,
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "observed_by": "github_actions",
        "validation_results": {
            "check_publisher_activation": env("CHECK_PUBLISHER_ACTIVATION", "passed_before_receipt"),
            "check_emergency_ai_templates": env("CHECK_EMERGENCY_AI_TEMPLATES", "covered_by_activation_runner"),
            "validate_emergency_ai_cases": env("VALIDATE_EMERGENCY_AI_CASES", "covered_by_activation_runner"),
            "check_site_mirror_dispatch": env("CHECK_SITE_MIRROR_DISPATCH", "covered_by_activation_runner"),
            "check_release_gate": env("CHECK_RELEASE_GATE", "covered_by_activation_runner"),
        },
        "dispatch_results": {
            "site_dispatch_attempted": site_dispatch_attempted,
            "site_dispatch_status": env(
                "SITE_DISPATCH_STATUS",
                "not_attempted_for_dry_run" if dry_run else "dispatch_step_completed",
            ),
            "site_workflow_run_url": env("SITE_WORKFLOW_RUN_URL") or None,
            "site_commit_sha": env("SITE_COMMIT_SHA") or None,
        },
        "release_gate_results": {
            "publisher_source_validity": env("PUBLISHER_SOURCE_VALIDITY", "covered_by_activation_runner"),
            "dispatch_readiness": env("DISPATCH_READINESS", "covered_by_activation_runner"),
            "site_mirror_validity": env("SITE_MIRROR_VALIDITY", "pending_site_workflow_evidence"),
            "public_display_verification": env("PUBLIC_DISPLAY_VERIFICATION", "pending_public_alias_evidence"),
            "governance_case_display_verification": env("GOVERNANCE_CASE_DISPLAY_VERIFICATION", "covered_by_release_gate"),
        },
        "notes": [
            "Generated automatically by tools/write_verification_run_receipt.py.",
            "This receipt records Publisher workflow evidence; Site evidence remains pending until Site workflow outputs are captured.",
        ],
    }


def main() -> int:
    output_dir = Path(env("RECEIPT_OUTPUT_DIR", str(DEFAULT_OUTPUT_DIR)))
    if not output_dir.is_absolute():
        output_dir = REPO_ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    receipt = build_receipt()
    run_class = safe_name(receipt["run_class"])
    run_id = safe_name(str(receipt["github_run_id"]))
    run_attempt = safe_name(str(receipt["github_run_attempt"]))
    output_path = output_dir / f"publisher-site-{run_class}-{run_id}-attempt-{run_attempt}.json"

    output_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote verification receipt: {output_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
