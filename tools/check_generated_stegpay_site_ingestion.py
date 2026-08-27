from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data/generated-stegpay-site-ingestion.json"

EXPECTED_RECEIPT_SHA = "687d06eb93693d0bd78f00cdefd465d23d92b54c0bbfa7bc0a04b1364f9a452f"
EXPECTED_PROPAGATION_SHA = "e59e71bf31879f0bf29a8356f8027304a94a4dee59d3c0be35c3ecc505e7cec9"
EXPECTED_CONSUMER_RECEIPT_SHA = "b8084ecc9821eb7738e4dccffd239185a072e0bc630e71c72906098a830cf515"
EXPECTED_GENERATED_UTC = "2026-08-27T11:58:18Z"


def main() -> int:
    value = json.loads(PATH.read_text(encoding="utf-8"))

    assert value["schema_version"] == "1.1"
    assert value["artifact_type"] == "publisher_generated_stegpay_site_ingestion"
    assert value["state"] == "INGESTED_TEST_EVIDENCE"
    assert value["source_repository"] == "StegVerse-Labs/Site"
    assert value["source_receipt_path"] == "data/generated-stegpay-propagations/latest/import_receipt.json"
    assert value["source_receipt_sha256"] == EXPECTED_RECEIPT_SHA
    assert value["source_generated_utc"] == EXPECTED_GENERATED_UTC
    assert value["source_propagation_sha256"] == EXPECTED_PROPAGATION_SHA
    assert value["source_consumer_receipt_sha256"] == EXPECTED_CONSUMER_RECEIPT_SHA

    event = value["event"]
    assert event["event_id"] == "09373107-5e4b-483e-85de-9e26c126fc0c"
    assert event["provider_id"] == "pi_test_123"
    assert event["test_only"] is True

    source_validation = value["source_validation"]
    assert source_validation["state"] == "VALIDATED"
    assert source_validation["historical_task"] == "SITE-0001-GENERATED-STEGPAY-PROPAGATION-IMPORT"
    assert source_validation["historical_task_state"] == "COMPLETE"

    interpretation = value["publisher_interpretation"]
    assert interpretation["evidence_ingested"] is True
    assert interpretation["publication_performed"] is False
    assert interpretation["production_payment_claimed"] is False
    assert interpretation["admissibility_claimed"] is False

    assert value["next_destinations"] == [
        "StegVerse-Labs/admissibility-wiki",
        "StegVerse-002/stegguardian-wiki",
    ]
    assert value["manual_user_action_required"] is False
    assert all(flag is False for flag in value["authority"].values())

    print("GENERATED_STEGPAY_SITE_INGESTION_VALID")
    print(f"source_receipt_sha256={EXPECTED_RECEIPT_SHA}")
    print(f"source_propagation_sha256={EXPECTED_PROPAGATION_SHA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
