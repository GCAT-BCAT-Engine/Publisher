import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


SCHEMA_PATH = Path(__file__).parents[1] / "schemas" / "publisher-governed-outbound-communication.v1.schema.json"


@pytest.fixture
def validator():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


@pytest.fixture
def valid_contract():
    digest = "a" * 64
    return {
        "schema": "stegverse.publisher.governed-outbound-communication/v1",
        "communication_event": {
            "event_id": "source-event-1",
            "source_system": "authoritative-history-source",
            "source_locator": "source://events/1",
            "observed_at": "2026-10-05T00:00:00Z",
            "content_sha256": digest,
            "media_type": "message/rfc822",
            "predecessor_event_ids": [],
        },
        "context_resolution": {
            "purpose": "reply to an existing communication",
            "policy_id": "purpose-context-policy-v1",
            "required_categories": [
                {
                    "category": "CORRESPONDENCE_HISTORY",
                    "disposition": "VERIFIED",
                    "evidence_refs": ["source://events/1"],
                }
            ],
        },
        "outbound_manifest": {
            "manifest_id": "outbound-1",
            "recipient": "recipient-ref",
            "channel": "email",
            "body_sha256": digest,
            "attachment_sha256": [],
            "requested_transport": "existing-authorized-email-transport",
            "authority_evidence_refs": ["authority://owner/1"],
            "composition_disposition": "ALLOW",
            "send_observation": {
                "observed": False,
                "provider_event_id": None,
                "sent_at": None,
                "receipt_refs": [],
            },
        },
    }


def assert_valid(validator, instance):
    validator.validate(instance)


def test_valid_unsent_contract_is_admitted(validator, valid_contract):
    assert_valid(validator, valid_contract)


def test_insufficient_evidence_cannot_allow_composition(validator, valid_contract):
    instance = copy.deepcopy(valid_contract)
    instance["context_resolution"]["required_categories"][0]["disposition"] = "INSUFFICIENT_EVIDENCE"
    with pytest.raises(ValidationError):
        validator.validate(instance)

    instance["outbound_manifest"]["composition_disposition"] = "FAIL_CLOSED"
    assert_valid(validator, instance)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("provider_event_id", "provider-message-1"),
        ("sent_at", "2026-10-05T00:01:00Z"),
    ],
)
def test_unobserved_send_cannot_carry_send_evidence(validator, valid_contract, field, value):
    instance = copy.deepcopy(valid_contract)
    instance["outbound_manifest"]["send_observation"][field] = value
    with pytest.raises(ValidationError):
        validator.validate(instance)
