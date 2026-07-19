from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data/generated-stegpay-site-ingestion.json"


def main() -> int:
    value = json.loads(PATH.read_text(encoding="utf-8"))

    assert value["schema_version"] == "1.0"
    assert value["artifact_type"] == "publisher_generated_stegpay_site_ingestion"
    assert value["state"] == "INGESTED_TEST_EVIDENCE"
    assert value["source_repository"] == "StegVerse-Labs/Site"
    assert value["source_status_path"] == "data/autonomy/generated-stegpay-integration-status.json"
    assert value["source_validation_path"] == "data/autonomy/generated-stegpay-integration-validation.json"
    assert value["source_canonical_sha256"] == "3b932c2f456d4dc7a8e5d98a7cd0199b5346649586de6da532b20aa042a79994"

    event = value["event"]
    assert event["event_id"] == "09373107-5e4b-483e-85de-9e26c126fc0c"
    assert event["provider_id"] == "pi_test_123"
    assert event["consumer_state"] == "deliverables_ready"
    assert event["producer_consumer_agreement"] is True
    assert event["matching_ledger_entries"] == 1
    assert event["test_only"] is True
    assert event["transport_is_authority"] is False

    source_validation = value["source_validation"]
    assert source_validation["state"] == "VALID"
    assert source_validation["downstream_ingestion_ready"] is True
    assert source_validation["failures"] == []

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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
