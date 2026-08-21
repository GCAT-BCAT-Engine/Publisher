#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "VERSION.json").read_text(encoding="utf-8"))
EXPECTED_REPOSITORY = "GCAT-BCAT-Engine/Publisher"

def fail(msg: str) -> None:
    raise SystemExit(f"COMPONENT_VERSION=FAIL\n- {msg}")

if DATA.get("schema_version") != "1.0.0": fail("schema_version must be 1.0.0")
if DATA.get("repository") != EXPECTED_REPOSITORY: fail("repository identity mismatch")
if not DATA.get("component_id") or not DATA.get("component_version"): fail("component identity/version required")
if DATA.get("version_stage") not in {"DEVELOPMENT","RELEASE_CANDIDATE","RELEASED"}: fail("unsupported version_stage")
if DATA.get("authority_effect") != "NONE": fail("version declaration may not grant authority")
for key in ("publication_authority","release_authority","activation_authority"):
    if DATA.get(key) is not False: fail(f"{key} must remain false")
release = DATA.get("release", {})
if DATA["version_stage"] == "RELEASED":
    if not release.get("tag") or not release.get("commit") or not release.get("release_evidence"): fail("RELEASED requires exact tag, commit, evidence")
elif release.get("tag") is not None or release.get("commit") is not None:
    fail("non-released component may not claim release tag/commit")
if DATA.get("activation", {}).get("state") == "ACTIVATED":
    fail("Publisher component cannot be ACTIVATED while canonical closure remains pending")
print("COMPONENT_VERSION=PASS")
print(f"COMPONENT_ID={DATA['component_id']}")
print(f"COMPONENT_VERSION_VALUE={DATA['component_version']}")
print(f"VERSION_STAGE={DATA['version_stage']}")
print("AUTHORITY_EFFECT=NONE")
