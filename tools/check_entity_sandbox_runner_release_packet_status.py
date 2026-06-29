from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "docs" / "ENTITY_SANDBOX_RUNNER_RELEASE_PACKET_STATUS.md"
JS = ROOT / "docs" / "ENTITY_SANDBOX_RUNNER_RELEASE_PACKET_STATUS.json"

REQUIRED_MD_TOKENS = [
    "StegGhost/entity-sandbox-runner",
    "admissibility_plane_activation_candidate",
    "publication_verification_surface_only",
    "pending_external_evidence",
    "Publisher must not become authority",
    "Publisher does not certify runtime admissibility",
    "Publisher does not issue commit-time permission",
]

REQUIRED_JSON_KEYS = [
    "source_repo",
    "release_goal",
    "publisher_status",
    "release_activation_state",
    "publisher_role",
    "source_inputs",
    "publisher_non_claims",
]


def main() -> None:
    errors: list[str] = []

    if not MD.exists():
        errors.append(f"missing:{MD}")
    else:
        text = MD.read_text(encoding="utf-8")
        for token in REQUIRED_MD_TOKENS:
            if token not in text:
                errors.append(f"missing_md_token:{token}")

    if not JS.exists():
        errors.append(f"missing:{JS}")
    else:
        data = json.loads(JS.read_text(encoding="utf-8"))
        for key in REQUIRED_JSON_KEYS:
            if key not in data:
                errors.append(f"missing_json_key:{key}")
        if data.get("source_repo") != "StegGhost/entity-sandbox-runner":
            errors.append("source_repo_mismatch")
        if data.get("publisher_status") != "installed_verification_surface":
            errors.append("publisher_status_must_remain_installed_verification_surface")
        if data.get("release_activation_state") != "pending_external_evidence":
            errors.append("release_activation_state_must_remain_pending_external_evidence")
        if data.get("publisher_role") != "publication_verification_surface_only":
            errors.append("publisher_role_must_remain_surface_only")

    if errors:
        print(json.dumps({"status": "failed", "errors": errors}, indent=2))
        raise SystemExit(1)

    print(json.dumps({"status": "ok", "checked": [str(MD), str(JS)]}, indent=2))


if __name__ == "__main__":
    main()
