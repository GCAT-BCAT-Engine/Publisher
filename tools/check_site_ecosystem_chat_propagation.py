#!/usr/bin/env python3
"""Validate Publisher's Site Ecosystem Chat propagation status."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "data" / "ecosystem-chat-site-propagation-status.json"
EXPECTED_REPOSITORY = "GCAT-BCAT-Engine/Publisher"
EXPECTED_SOURCE = "StegVerse-Labs/Site"
ALLOWED_STATES = {"PENDING_SITE_ACTIVATION", "VERIFIED_INGESTION_READY"}
FORBIDDEN_AUTHORITIES = {
    "publication_authority",
    "release_authority",
    "activation_authority",
    "admissibility_authority",
    "execution_authority",
}
DESTINATION_BLOCKER = "publisher_destination_not_declared_by_site"


def fail(message: str) -> None:
    raise SystemExit(f"DENY: {message}")


def main() -> None:
    if not STATUS.exists():
        fail(f"missing {STATUS.relative_to(ROOT)}")
    payload = json.loads(STATUS.read_text(encoding="utf-8"))
    if payload.get("repository") != EXPECTED_REPOSITORY:
        fail("repository identity mismatch")
    if payload.get("source_repository") != EXPECTED_SOURCE:
        fail("source repository mismatch")
    if payload.get("source_hash_valid") is not True:
        fail("source hash is not valid")
    if payload.get("manual_user_action_required") is not False:
        fail("manual user action boundary violated")

    state = payload.get("state")
    if state not in ALLOWED_STATES:
        fail(f"unsupported state {state!r}")
    blockers = payload.get("blockers")
    if not isinstance(blockers, list):
        fail("blockers must be a list")
    if state == "PENDING_SITE_ACTIVATION" and not blockers:
        fail("pending state lacks an exact blocker")
    if state == "VERIFIED_INGESTION_READY" and blockers:
        fail("ready state retains blockers")
    if state == "VERIFIED_INGESTION_READY" and payload.get("source_state") != "READY_FOR_DOWNSTREAM_INGESTION":
        fail("ready ingestion is not backed by Site ready state")

    destination_declared = payload.get("destination_declared")
    if destination_declared is True:
        if DESTINATION_BLOCKER in blockers:
            fail("declared destination retains undeclared-destination blocker")
    elif destination_declared is False:
        if state != "PENDING_SITE_ACTIVATION":
            fail("undeclared destination cannot be ingestion ready")
        if DESTINATION_BLOCKER not in blockers:
            fail("undeclared destination lacks exact blocker")
    else:
        fail("destination_declared must be boolean")

    if not isinstance(payload.get("next_executable_task"), str):
        fail("next executable task missing")
    if not isinstance(payload.get("release_condition"), str):
        fail("release condition missing")

    authority = payload.get("authority")
    if not isinstance(authority, dict):
        fail("authority boundary missing")
    true_forbidden = sorted(key for key in FORBIDDEN_AUTHORITIES if authority.get(key) is not False)
    if true_forbidden:
        fail(f"authority flags must remain false: {true_forbidden}")

    print(json.dumps({
        "state": state,
        "destination_declared": destination_declared,
        "blockers": blockers,
        "next_executable_task": payload["next_executable_task"],
        "release_condition": payload["release_condition"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
