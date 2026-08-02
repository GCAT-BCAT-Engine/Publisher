#!/usr/bin/env python3
"""Write a fail-closed runtime receipt for the GCAT capacity validation workflow."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        return "unavailable"
    return result.stdout.strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("reports/gcat-capacity-runtime-receipt.json"))
    parser.add_argument("--result", choices=("COMPLETE", "FAILED", "BLOCKED", "REVIEW_REQUIRED"), required=True)
    parser.add_argument("--validator", action="append", default=[], help="Validator command that was executed.")
    parser.add_argument("--failure", action="append", default=[], help="Failure or review-required reason.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifests = [
        ROOT / "generated/gcat-capacity/manifest.json",
        ROOT / "generated/gcat-capacity-sensitivity/manifest.json",
        ROOT / "generated/gcat-capacity-timeseries/manifest.json",
    ]
    manifest_records: List[Dict[str, object]] = []
    missing = []
    for path in manifests:
        if path.is_file():
            manifest_records.append({
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            })
        else:
            missing.append(str(path.relative_to(ROOT)))

    result = args.result
    failures = list(args.failure)
    if result == "COMPLETE" and missing:
        result = "FAILED"
        failures.append("Missing required generated manifests: " + ", ".join(missing))

    receipt = {
        "schema_version": "1.0.0",
        "receipt_id": "gcat-capacity-runtime-validation",
        "task_id": "GCAT-CAP-008",
        "repository": os.environ.get("GITHUB_REPOSITORY", "GCAT-BCAT-Engine/Publisher"),
        "ref": os.environ.get("GITHUB_REF", git_output("branch", "--show-current")),
        "commit_sha": os.environ.get("GITHUB_SHA", git_output("rev-parse", "HEAD")),
        "workflow": os.environ.get("GITHUB_WORKFLOW", "local"),
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "workflow_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", "local"),
        "result": result,
        "validators": args.validator,
        "failures": failures,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "working_tree_status": git_output("status", "--porcelain"),
        },
        "generated_manifests": manifest_records,
        "missing_manifests": missing,
        "claim_boundary": [
            "COMPLETE proves only repository-local synthetic generation and validator success on the recorded commit.",
            "It does not prove empirical calibration, mathematical peer review, publication readiness, release, deployment, or downstream activation.",
            "Omega > 1 remains a modeled overload classification and is not automatic proof of drift."
        ],
        "next_state": "REVIEW_REQUIRED" if result == "COMPLETE" else "RETRY",
        "next_task": "Inspect workflow jobs, logs, and uploaded artifact; then record review disposition in PR #5 and Issue #6."
    }

    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if result == args.result else 1


if __name__ == "__main__":
    raise SystemExit(main())
