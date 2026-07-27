#!/usr/bin/env python3
"""Validate Publisher's bounded Admissible Resolution awareness receipt."""

from __future__ import annotations

import json
from pathlib import Path

RECEIPT = Path("data/admissible-resolution-awareness-receipt.json")
EXPECTED_IDS = ["T-060", "T-061", "T-062", "T-063", "T-064", "T-065"]
EXPECTED_FALSE = [
    "publication_authorized",
    "release_authorized",
    "execution_authorized",
    "custody_recorded",
    "certification_authority_created",
    "admissibility_determined",
]


def main() -> int:
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    errors: list[str] = []

    checks = {
        "receipt_type": data.get("receipt_type") == "admissible_resolution_publisher_awareness",
        "repository": data.get("repository") == "GCAT-BCAT-Engine/Publisher",
        "source_repository": data.get("source_repository") == "Admissible-Existence/TT",
        "decision_id": data.get("decision_id") == "AR-CHAIN-001",
        "source_packet_hash": data.get("source_packet_canonical_sha256") == "sha256:d01f86e79a0370035091c6472986186a4e2ce7c5304976b597fcef8a14da8bd6",
        "registry_family": data.get("registry", {}).get("family") == "Resolution",
        "registry_ids": data.get("registry", {}).get("transition_ids") == EXPECTED_IDS,
        "registry_total": data.get("registry", {}).get("expected_total_transition_elements") == 76,
        "node_sufficiency": data.get("verified_chain", {}).get("allocated_nodes") >= data.get("verified_chain", {}).get("required_nodes"),
        "resolution_result": data.get("verified_chain", {}).get("result") == "RESOLUTION_SATISFIED",
        "destination_state": data.get("destination_state") == "AWARENESS_RECEIPT_PERSISTED",
        "manual_user_action": data.get("manual_user_action_required") is False,
    }

    for name, passed in checks.items():
        if not passed:
            errors.append(name)

    for field in EXPECTED_FALSE:
        if data.get(field) is not False:
            errors.append(f"authority:{field}")

    if errors:
        print(json.dumps({"result": "FAIL_CLOSED", "errors": errors}, indent=2))
        return 1

    print(json.dumps({
        "result": "AWARENESS_RECEIPT_VALID",
        "decision_id": data["decision_id"],
        "source_packet_canonical_sha256": data["source_packet_canonical_sha256"],
        "publication_authorized": False,
        "release_authorized": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
