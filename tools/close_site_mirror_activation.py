#!/usr/bin/env python3
"""Close Publisher-to-Site mirror activation from workflow evidence artifacts.

This script is designed for GitHub Actions. It looks for the newest Publisher
verification receipt artifact and the newest Site mirror evidence artifact. When
both are present, it updates Publisher-side tracker/status files to activated.

It does not fabricate evidence. If required artifacts are missing, it leaves the
repo in a pending state and exits successfully so scheduled automation can try
again on the next run.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
TRACKER_PATH = REPO_ROOT / "docs" / "verification-tracker.md"
STATUS_PATH = REPO_ROOT / "docs" / "activation-status.md"
CLOSURE_DIR = REPO_ROOT / "docs" / "mirror-activation-closures"

PUBLISHER_REPOSITORY = "GCAT-BCAT-Engine/Publisher"
SITE_REPOSITORY = "StegVerse-Labs/Site"
PUBLISHER_ARTIFACT_PREFIX = "publisher-site-verification-receipt"
SITE_ARTIFACT_PREFIX = "site-mirror-evidence"

API_ROOT = "https://api.github.com"


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def token() -> str:
    return env("GH_TOKEN") or env("GITHUB_TOKEN")


def request_json(url: str) -> dict[str, Any]:
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token():
        req.add_header("Authorization", f"Bearer {token()}")
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def download(url: str, target: Path) -> None:
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token():
        req.add_header("Authorization", f"Bearer {token()}")
    with urllib.request.urlopen(req, timeout=60) as response:
        target.write_bytes(response.read())


def list_artifacts(repository: str) -> list[dict[str, Any]]:
    url = f"{API_ROOT}/repos/{repository}/actions/artifacts?per_page=100"
    data = request_json(url)
    artifacts = data.get("artifacts", [])
    return [artifact for artifact in artifacts if not artifact.get("expired", False)]


def newest_artifact(repository: str, prefix: str) -> dict[str, Any] | None:
    matches = [artifact for artifact in list_artifacts(repository) if str(artifact.get("name", "")).startswith(prefix)]
    if not matches:
        return None
    matches.sort(key=lambda artifact: str(artifact.get("created_at", "")), reverse=True)
    return matches[0]


def extract_artifact(repository: str, artifact: dict[str, Any], target_dir: Path) -> list[Path]:
    archive_url = artifact.get("archive_download_url")
    if not archive_url:
        return []
    zip_path = target_dir / f"{repository.replace('/', '-')}-{artifact['id']}.zip"
    download(str(archive_url), zip_path)
    extract_dir = target_dir / f"extracted-{artifact['id']}"
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(extract_dir)
    return [path for path in extract_dir.rglob("*") if path.is_file()]


def load_first_json(paths: list[Path], required_name_fragment: str | None = None) -> dict[str, Any] | None:
    for path in paths:
        if path.suffix.lower() != ".json":
            continue
        if required_name_fragment and required_name_fragment not in path.name:
            continue
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
    return None


def load_site_state(paths: list[Path]) -> dict[str, Any] | None:
    for path in paths:
        if path.name != "SITE_MIRROR_LIVE_EVIDENCE_STATE.json":
            continue
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
    return None


def artifact_url(repository: str, artifact: dict[str, Any]) -> str:
    return f"https://github.com/{repository}/actions/runs/{artifact.get('workflow_run', {}).get('id', 'unknown')}#artifacts"


def evidence_ready(publisher_receipt: dict[str, Any], site_state: dict[str, Any]) -> tuple[bool, list[str]]:
    missing: list[str] = []
    if publisher_receipt.get("receipt_type") != "publisher_to_site_verification_run":
        missing.append("publisher receipt_type")
    if publisher_receipt.get("dry_run") is True:
        missing.append("publisher live dispatch receipt")
    dispatch = publisher_receipt.get("dispatch_results", {})
    if not dispatch.get("site_dispatch_attempted"):
        missing.append("publisher site_dispatch_attempted")
    if str(dispatch.get("site_dispatch_status", "")).lower() not in {"dispatch_request_accepted", "dispatch_step_completed"}:
        missing.append("publisher dispatch accepted status")

    evidence = site_state.get("evidence", {})
    required_site_fields = [
        "site_mirror_workflow_url",
        "site_mirror_commit_sha",
        "manifest_source_repository",
        "manifest_source_ref",
        "manifest_source_of_truth",
        "alias_verification_results",
    ]
    for field in required_site_fields:
        value = str(evidence.get(field, "")).strip()
        if value in {"", "PENDING", "TODO", "TBD", "UNKNOWN", "None", "null"}:
            missing.append(f"site {field}")

    if site_state.get("activation_state") == "activated" and site_state.get("live_activation_verified") is not True:
        missing.append("site activation state/boolean mismatch")

    return not missing, missing


def sanitize(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.:/#-]+", "-", value).strip("-") or "unknown"


def write_closure_receipt(publisher_artifact: dict[str, Any], site_artifact: dict[str, Any], publisher_receipt: dict[str, Any], site_state: dict[str, Any]) -> Path:
    CLOSURE_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = CLOSURE_DIR / f"publisher-site-mirror-closure-{timestamp}.json"
    payload = {
        "schema": "stegverse.publisher.site_mirror.closure.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "activation_state": "activated",
        "publisher_repository": PUBLISHER_REPOSITORY,
        "site_repository": SITE_REPOSITORY,
        "publisher_artifact": {
            "id": publisher_artifact.get("id"),
            "name": publisher_artifact.get("name"),
            "url": artifact_url(PUBLISHER_REPOSITORY, publisher_artifact),
        },
        "site_artifact": {
            "id": site_artifact.get("id"),
            "name": site_artifact.get("name"),
            "url": artifact_url(SITE_REPOSITORY, site_artifact),
        },
        "publisher_run_url": publisher_receipt.get("github_run_url"),
        "site_workflow_url": site_state.get("evidence", {}).get("site_mirror_workflow_url"),
        "site_commit_sha": site_state.get("evidence", {}).get("site_mirror_commit_sha"),
        "alias_verification_results": site_state.get("evidence", {}).get("alias_verification_results"),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def update_tracker(closure_path: Path, publisher_artifact: dict[str, Any], site_artifact: dict[str, Any], publisher_receipt: dict[str, Any], site_state: dict[str, Any]) -> None:
    closure_rel = closure_path.relative_to(REPO_ROOT)
    publisher_url = artifact_url(PUBLISHER_REPOSITORY, publisher_artifact)
    site_url = artifact_url(SITE_REPOSITORY, site_artifact)
    content = f"""# Publisher to Site Verification Tracker

## Objective

Track the operational verification of the Publisher-to-Site mirror path after policy, dispatch automation, activation-runner, release-gate, Site handoff, Publisher handoff, automated receipt artifacts, and automated closure were added.

## Status

```text
status: activated
```

## Closure Receipt

```text
{closure_rel}
```

## Verified Evidence

```text
publisher_workflow_run_url: {publisher_receipt.get('github_run_url')}
publisher_verification_receipt_artifact: {publisher_url}
publisher_live_dispatch_workflow_url: {publisher_receipt.get('github_run_url')}
site_mirror_workflow_url: {site_state.get('evidence', {}).get('site_mirror_workflow_url')}
site_mirror_commit_sha: {site_state.get('evidence', {}).get('site_mirror_commit_sha')}
manifest_source_repository: {site_state.get('evidence', {}).get('manifest_source_repository')}
manifest_source_ref: {site_state.get('evidence', {}).get('manifest_source_ref')}
manifest_source_of_truth: {site_state.get('evidence', {}).get('manifest_source_of_truth')}
alias_verification_results: {site_state.get('evidence', {}).get('alias_verification_results')}
site_evidence_artifact: {site_url}
site_evidence_packet_completion_commit: {site_state.get('evidence', {}).get('site_evidence_packet_completion_commit', 'captured_by_site_artifact')}
site_live_evidence_state_completion_commit: {site_state.get('evidence', {}).get('site_live_evidence_state_completion_commit', 'captured_by_site_artifact')}
publisher_verification_tracker_activation_commit: generated_by_closure_workflow
publisher_activation_status_update_commit: generated_by_closure_workflow
```

## Activation Closure

The Publisher-to-Site mirror activation is marked activated because the closure workflow found both required artifact classes and verified their minimum evidence fields:

```text
Publisher artifact prefix: {PUBLISHER_ARTIFACT_PREFIX}
Site artifact prefix: {SITE_ARTIFACT_PREFIX}
Closure receipt: {closure_rel}
```

## Release Gate

Site paper display may be treated as current only for the evidence represented in the closure receipt above. Future mirror runs must produce their own Publisher and Site evidence artifacts.

## Relevant Files

```text
.github/workflows/dispatch-site-mirror.yml
.github/workflows/close-site-mirror-activation.yml
tools/write_verification_run_receipt.py
tools/close_site_mirror_activation.py
docs/PUBLISHER_MIRROR_HANDOFF.md
docs/activation-status.md
{closure_rel}
StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md
StegVerse-Labs/Site/docs/SITE_MIRROR_EVIDENCE_PACKET.md
StegVerse-Labs/Site/docs/SITE_MIRROR_LIVE_EVIDENCE_STATE.json
```

## Archive Readiness

This tracker contains the activated evidence closure and no longer requires older chat context for forward progress.
"""
    TRACKER_PATH.write_text(content, encoding="utf-8")


def update_status(closure_path: Path, publisher_artifact: dict[str, Any], site_artifact: dict[str, Any]) -> None:
    closure_rel = closure_path.relative_to(REPO_ROOT)
    content = f"""# Publisher Activation Status

## Current State

```text
activation_state: activated
repository: GCAT-BCAT-Engine/Publisher
activation_target: Publisher to Site mirror dispatch
site_target: StegVerse-Labs/Site
closure_receipt: {closure_rel}
```

## What Is Complete

```text
Publisher source validation exists
Emergency AI case validation exists
Site mirror dispatch workflow exists
Dispatch workflow runs on qualifying push to main
Dispatch workflow writes verification receipt artifacts automatically
Site mirror workflow writes Site evidence artifacts automatically
Automated closure workflow found Publisher and Site evidence artifacts
Automated closure workflow wrote activation closure receipt
Publisher verification tracker is marked activated
Publisher activation status is marked activated
```

## Activation Boundary

Repo activation is complete for the evidence captured in:

```text
{closure_rel}
```

The closure is evidence-bound to:

```text
Publisher artifact: {artifact_url(PUBLISHER_REPOSITORY, publisher_artifact)}
Site artifact: {artifact_url(SITE_REPOSITORY, site_artifact)}
```

## Current Validation Contract

Publisher activation remains guarded by:

```text
python tools/check_publisher_activation.py
python tools/close_site_mirror_activation.py
```

## Activation Evidence Files

```text
docs/verification-tracker.md
docs/activation-status.md
docs/PUBLISHER_MIRROR_HANDOFF.md
tools/write_verification_run_receipt.py
tools/close_site_mirror_activation.py
github/workflows/dispatch-site-mirror.yml
github/workflows/close-site-mirror-activation.yml
{closure_rel}
StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md
StegVerse-Labs/Site/docs/SITE_MIRROR_EVIDENCE_PACKET.md
StegVerse-Labs/Site/docs/SITE_MIRROR_LIVE_EVIDENCE_STATE.json
```

Note: workflow paths are displayed without the leading dot. The actual repository paths include the leading dot.

## Archive Readiness

This activation status contains the activated closure evidence and no longer requires prior chat context for forward progress.
"""
    STATUS_PATH.write_text(content, encoding="utf-8")


def main() -> int:
    with TemporaryDirectory() as temp_name:
        temp_dir = Path(temp_name)
        publisher_artifact = newest_artifact(PUBLISHER_REPOSITORY, PUBLISHER_ARTIFACT_PREFIX)
        site_artifact = newest_artifact(SITE_REPOSITORY, SITE_ARTIFACT_PREFIX)

        if not publisher_artifact or not site_artifact:
            print("activation closure pending: required artifacts not found")
            if not publisher_artifact:
                print(f"missing artifact prefix: {PUBLISHER_REPOSITORY}/{PUBLISHER_ARTIFACT_PREFIX}")
            if not site_artifact:
                print(f"missing artifact prefix: {SITE_REPOSITORY}/{SITE_ARTIFACT_PREFIX}")
            return 0

        publisher_paths = extract_artifact(PUBLISHER_REPOSITORY, publisher_artifact, temp_dir)
        site_paths = extract_artifact(SITE_REPOSITORY, site_artifact, temp_dir)
        publisher_receipt = load_first_json(publisher_paths)
        site_state = load_site_state(site_paths)

        if not publisher_receipt or not site_state:
            print("activation closure pending: artifacts did not contain required JSON evidence")
            return 0

        ready, missing = evidence_ready(publisher_receipt, site_state)
        if not ready:
            print("activation closure pending: missing evidence: " + ", ".join(missing))
            return 0

        closure_path = write_closure_receipt(publisher_artifact, site_artifact, publisher_receipt, site_state)
        update_tracker(closure_path, publisher_artifact, site_artifact, publisher_receipt, site_state)
        update_status(closure_path, publisher_artifact, site_artifact)
        print(f"activated Publisher-to-Site mirror using closure receipt: {closure_path.relative_to(REPO_ROOT)}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
