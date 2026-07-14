#!/usr/bin/env python3
"""Mirror canonical SDK system-boundary status into Publisher without manual copying."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Mapping

SOURCE = "https://raw.githubusercontent.com/StegVerse-org/StegVerse-SDK/main/evidence/system-boundary-downstream-status.v0.1.json"
OUTPUT = Path(__file__).resolve().parents[1] / "data/system-boundary-status.v0.1.json"
TARGET = "GCAT-BCAT-Engine/Publisher"
REQUIRED_FALSE = (
    "production_binding_enabled",
    "release_authorized",
    "execution_authority_granted",
    "custody_transferred",
    "admissibility_determined",
)


def validate_packet(packet: Mapping[str, Any]) -> None:
    if packet.get("schema_version") != "stegverse.system_boundary.downstream_status.v0.1":
        raise ValueError("unsupported downstream status schema")
    if packet.get("status_only") is not True or TARGET not in packet.get("targets", []):
        raise ValueError("Publisher is not an authorized status-only target")
    for key in REQUIRED_FALSE:
        if packet.get(key) is not False:
            raise ValueError(f"{key} must remain false")
    verified = packet.get("verified")
    propagation = packet.get("downstream_propagation_allowed")
    state = packet.get("activation_state")
    if state == "VERIFIED":
        if verified is not True or propagation is not True:
            raise ValueError("VERIFIED flags are inconsistent")
    elif verified is not False or propagation is not False:
        raise ValueError("non-VERIFIED status cannot propagate")


def fetch_packet() -> dict[str, Any]:
    request = urllib.request.Request(SOURCE, headers={"User-Agent": "StegVerse-Publisher-status-sync"})
    with urllib.request.urlopen(request, timeout=30) as response:
        packet = json.load(response)
    validate_packet(packet)
    return packet


def main() -> int:
    try:
        packet = fetch_packet()
    except (urllib.error.URLError, TimeoutError):
        print("Transient retrieval failure; retaining prior validated Publisher state.")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    if OUTPUT.exists() and OUTPUT.read_text(encoding="utf-8") == rendered:
        print("System-boundary status unchanged.")
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print("System-boundary status updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
