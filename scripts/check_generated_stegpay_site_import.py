#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "data/generated-stegpay-site-import/latest/site_import_receipt.json"
STATUS = ROOT / "data/generated-stegpay-publication-status.json"
EXPECTED_RECEIPT_HASH = "45e8e8849f6d0967de66da6bc45f874c33fcea703a80ba165f45ffa6fecd81d1"
EXPECTED_PROPAGATION_HASH = "aecfd09a016e1daaa32b66f0e7aa2bc2681edc70be14f25637fa95df2a1468e3"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"object required: {path}")
    return value


def digest(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"GENERATED_STEGPAY_PUBLISHER_IMPORT=FAIL: {message}")


def main() -> int:
    for path in (RECEIPT, STATUS):
        if not path.is_file():
            fail(f"missing {path.relative_to(ROOT)}")

    receipt = load(RECEIPT)
    status = load(STATUS)
    receipt_hash = digest(receipt)
    if receipt_hash != EXPECTED_RECEIPT_HASH:
        fail(f"Site receipt hash mismatch: {receipt_hash}")
    if receipt.get("state") != "VALIDATED":
        fail("Site receipt is not VALIDATED")
    if receipt.get("propagation_hash_sha256") != EXPECTED_PROPAGATION_HASH:
        fail("unexpected propagation hash")
    if status.get("source_receipt_hash_sha256") != receipt_hash:
        fail("Publisher status does not bind Site receipt")
    if status.get("propagation_hash_sha256") != EXPECTED_PROPAGATION_HASH:
        fail("Publisher status propagation hash mismatch")
    if status.get("state") != "VERIFIED_TEST_EVIDENCE_IMPORTED":
        fail("Publisher projection state mismatch")
    if status.get("event_id") != receipt.get("event_id") or status.get("provider_id") != receipt.get("provider_id"):
        fail("Publisher identity mismatch")
    if status.get("test_only") is not True or receipt.get("test_only") is not True:
        fail("test-only posture missing")
    for field in ("publication_authorized", "release_authorized", "custody_recorded", "execution_authorized", "payment_is_entitlement", "transport_is_authority"):
        if status.get(field) is not False:
            fail(f"authority boundary violated: {field}")
    for field in ("authority_effect", "activation_effect", "publication_effect", "release_effect"):
        if receipt.get(field) is not False:
            fail(f"Site receipt authority boundary violated: {field}")

    print("GENERATED_STEGPAY_PUBLISHER_IMPORT=PASS")
    print(f"site_receipt_hash={receipt_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
