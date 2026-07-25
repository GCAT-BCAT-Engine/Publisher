import copy
import unittest

from tools.check_publication_authority_envelope import (
    PublicationAuthorityError,
    validate_envelope,
)


def envelope(action="INSPECT"):
    return {
        "schema_version": "1.0.0",
        "artifact_id": "manifest-receipt-boundary",
        "artifact_version": "0.3",
        "visibility_state": "PUBLICLY_VISIBLE",
        "process_state": "REVIEW_ONLY",
        "claim_authority": False,
        "publication_authority": False,
        "attribution_authority": False,
        "public_association_authority": False,
        "endorsement": "NONE",
        "compatibility": "NONE",
        "interoperability": "NONE",
        "external_references": [
            {"name": "GLM", "association_status": "REFERENCE_ONLY"},
            {"name": "EVIDE", "association_status": "REFERENCE_ONLY"},
        ],
        "requested_publication_action": action,
    }


class PublicationAuthorityEnvelopeTests(unittest.TestCase):
    def test_public_visibility_allows_inspection_without_authority(self):
        result = validate_envelope(envelope())
        self.assertEqual(result["publisher_decision"], "ALLOW")
        self.assertFalse(result["visibility_was_authority_source"])
        self.assertEqual(len(result["envelope_sha256"]), 64)

    def test_public_visibility_does_not_allow_publication(self):
        result = validate_envelope(envelope("PUBLISH"))
        self.assertEqual(result["publisher_decision"], "DENY")
        self.assertIn("publication_authority", result["publisher_decision_reason"])

    def test_public_visibility_does_not_allow_attribution(self):
        result = validate_envelope(envelope("ATTRIBUTE"))
        self.assertEqual(result["publisher_decision"], "DENY")
        self.assertIn("attribution_authority", result["publisher_decision_reason"])

    def test_review_only_authority_grant_fails_closed(self):
        value = envelope()
        value["publication_authority"] = True
        with self.assertRaisesRegex(PublicationAuthorityError, "review-only"):
            validate_envelope(value)

    def test_review_only_external_claim_fails_closed(self):
        value = envelope()
        value["interoperability"] = "ASSERTED"
        with self.assertRaisesRegex(PublicationAuthorityError, "external claims"):
            validate_envelope(value)

    def test_visibility_cannot_be_authority_source(self):
        value = envelope()
        value["authority_source"] = "VISIBILITY"
        with self.assertRaisesRegex(PublicationAuthorityError, "visibility"):
            validate_envelope(value)

    def test_external_association_requires_authority(self):
        value = envelope("ASSOCIATE_EXTERNAL")
        value["external_references"][0]["association_status"] = "AUTHORIZED_ASSOCIATION"
        with self.assertRaisesRegex(PublicationAuthorityError, "public_association_authority"):
            validate_envelope(value)

    def test_adopted_artifact_with_explicit_publication_authority_can_publish(self):
        value = envelope("PUBLISH")
        value["process_state"] = "ADOPTED"
        value["publication_authority"] = True
        value["authority_source"] = "delegation:artifact-owner-v1"
        result = validate_envelope(value)
        self.assertEqual(result["publisher_decision"], "ALLOW")

    def test_hash_is_deterministic(self):
        first = validate_envelope(envelope())
        second = validate_envelope(copy.deepcopy(envelope()))
        self.assertEqual(first["envelope_sha256"], second["envelope_sha256"])

    def test_tampered_hash_is_rejected(self):
        value = validate_envelope(envelope())
        value.pop("publisher_decision")
        value.pop("publisher_decision_reason")
        value.pop("visibility_was_authority_source")
        value["artifact_version"] = "tampered"
        with self.assertRaisesRegex(PublicationAuthorityError, "hash mismatch"):
            validate_envelope(value)

    def test_none_identity_is_rejected(self):
        value = envelope()
        value["artifact_id"] = None
        with self.assertRaisesRegex(PublicationAuthorityError, "artifact_id"):
            validate_envelope(value)


if __name__ == "__main__":
    unittest.main()
