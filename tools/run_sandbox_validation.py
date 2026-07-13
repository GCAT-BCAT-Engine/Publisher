#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "templates" / "sandbox-first" / "publisher.sandbox-profile.json"
REPORT = ROOT / "reports" / "sandbox-first-validation.report.json"


def main() -> int:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    results = []
    status = "PASS"
    with tempfile.TemporaryDirectory(prefix="publisher-st017-") as tmp:
        sandbox = Path(tmp) / "repo"
        excludes = set(profile.get("exclude", []))
        shutil.copytree(ROOT, sandbox, ignore=shutil.ignore_patterns(*excludes))
        (sandbox / "reports").mkdir(parents=True, exist_ok=True)
        for command in profile["commands"]:
            started = time.monotonic()
            try:
                run = subprocess.run(
                    command["argv"], cwd=sandbox, text=True,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    timeout=profile.get("timeout_seconds", 300), check=False,
                )
                timed_out = False
                exit_code = run.returncode
                stdout = run.stdout[-4000:]
                stderr = run.stderr[-4000:]
            except subprocess.TimeoutExpired as exc:
                timed_out = True
                exit_code = None
                stdout = (exc.stdout or "")[-4000:] if isinstance(exc.stdout, str) else ""
                stderr = (exc.stderr or "")[-4000:] if isinstance(exc.stderr, str) else ""
            passed = not timed_out and exit_code == command.get("expected_exit", 0)
            results.append({
                "id": command["id"], "argv": command["argv"],
                "expected_exit": command.get("expected_exit", 0),
                "actual_exit": exit_code, "passed": passed,
                "timed_out": timed_out,
                "duration_seconds": round(time.monotonic() - started, 3),
                "stdout_tail": stdout, "stderr_tail": stderr,
            })
            if not passed:
                status = "FAIL"
                break
    report = {
        "schema_version": "1.0.0",
        "record_type": "sandbox_validation_report",
        "repository": profile["repository"],
        "profile_id": profile["profile_id"],
        "sandbox_status": status,
        "github_actions_status": "NOT_OBSERVED",
        "public_output_status": "NOT_APPLICABLE",
        "results": results,
        "non_claims": {
            "release_authority": False,
            "publication_authority": False,
            "downstream_authority": False,
            "admissibility": False
        }
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"PUBLISHER ST-017 SANDBOX: {status}")
    for result in results:
        print(f"{result['id']}: {'PASS' if result['passed'] else 'FAIL'}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
