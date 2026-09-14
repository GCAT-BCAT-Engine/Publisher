from __future__ import annotations
import copy, json, tempfile, unittest
from pathlib import Path

from publisher.intr_artifact_transfer import (
    MIR_ROUNDTRIP_BINDING_PROFILE,
    SDK_COMPLETION_CAPSULE_PROFILE,
    PublisherArtifactTransferError,
    canonical_json,
    process_artifact_transfer,
    sha256_value,
    verify_artifact_return,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_HASH = "1" * 64
RETAINED_PACKET_HASH = "2" * 64
RESPONSE_TO = "mir-node-mirror-runtime-return-001"


def bundle():
    value = json.loads((ROOT / "tests/fixtures/document-export/admitted.json").read_text())
    value["authorization"]["expires_at"] = "2099-12-31T23:59:59Z"
    unhashed = copy.deepcopy(value)
    unhashed.pop("export_sha256", None)
    value["export_sha256"] = sha256_value(unhashed)
    return value


def transfer():
    b = bundle()
    return {
        "schema": "stegverse.publisher.artifact-transfer/v1",
        "transfer_id": "kv-publisher-transfer-test-001",
        "operation": "TRANSFER",
        "export_bundle": b,
        "export_sha256": b["export_sha256"],
        "requested_formats": b["requested_formats"],
        "authorization_ref": b["authorization"]["authority_ref"],
        "publication_authorized": False,
        "release_authorized": False,
        "execution_authorized": False,
        "authority_effect": "NONE",
    }


def completion_block():
    return {
        "direction": "SOUTH",
        "initiator": {"class": "site_sdk_processing_handoff", "ref": "StegVerse-Labs/Site#1319"},
        "publisher": {
            "stage": "PUBLISHER",
            "required": True,
            "package_profile": "stegverse.publisher.evidence-report-package/v1",
        },
        "egress": {
            "final_stegverse_transition_surface": "LLM_ADAPTER",
            "transport": "INTERLOCK_INTR",
            "far_side_transition_required": True,
        },
    }


def completion_capsule(*, publisher_required: bool = True):
    completion = completion_block()
    completion["publisher"]["required"] = publisher_required
    return {
        "profile": SDK_COMPLETION_CAPSULE_PROFILE,
        "manifest_hash": "sha256:" + MANIFEST_HASH,
        "completion_hash": sha256_value(completion),
        "response_to": RESPONSE_TO,
        "retained_packet_sha256": "sha256:" + RETAINED_PACKET_HASH,
        "completion": completion,
        "declarations": {
            "publisher_required": publisher_required,
            "publisher_package_profile": "stegverse.publisher.evidence-report-package/v1",
            "final_stegverse_side_egress_surface": "LLM_ADAPTER",
            "interlock_intr_egress_required": True,
            "far_side_transition_required": True,
        },
        "authority_effect": "NONE",
    }


def roundtrip_binding(**overrides):
    capsule = completion_capsule()
    value = {
        "profile": MIR_ROUNDTRIP_BINDING_PROFILE,
        "goal_task_id": "MIR-CONNECTION-ROUNDTRIP-TECHNICAL-GUIDE-001",
        "cosv_id": "50000000100000",
        "publisher_transition": "PUBLISHER_ARTIFACT_RETURN_PRODUCED",
        "manifest_hash": "sha256:" + MANIFEST_HASH,
        "completion_hash": capsule["completion_hash"],
        "response_to": RESPONSE_TO,
        "retained_packet_sha256": "sha256:" + RETAINED_PACKET_HASH,
        "downstream_completion_capsule": capsule,
        "sdk_processor_state": {
            "state": "SDK_MANIFEST_SELECTED_PROCESSING_EXECUTED",
            "processor_result_observed": True,
            "processor_result_ref": "StegVerse-org/StegVerse-SDK#240",
        },
        "publisher_transition_observed": False,
        "sdk_return_binding_observed": False,
        "final_stegverse_side_egress_transition_observed": False,
        "interlock_intr_egress_observed": False,
        "far_side_transition_observed": False,
        "authentic_external_mir_endpoint_substitution_observed": False,
        "communication_complete": False,
        "authority_effect": "NONE",
    }
    value.update(overrides)
    return value


def transfer_with_roundtrip_binding(**binding_overrides):
    value = transfer()
    value["roundtrip_binding"] = roundtrip_binding(**binding_overrides)
    value["transfer_id"] = "mir-roundtrip-publisher-transfer-001"
    return value


class PublisherArtifactTransferTests(unittest.TestCase):
    def test_exact_transfer_renders_and_returns_reconstructable_artifacts(self):
        raw = canonical_json(transfer()).encode()
        with tempfile.TemporaryDirectory() as td:
            result, returned = process_artifact_transfer(raw, Path(td))
        parsed = verify_artifact_return(returned)
        self.assertEqual(parsed, result)
        self.assertFalse(result["publication_authorized"])
        self.assertEqual({x["format"] for x in result["artifacts"]}, set(bundle()["requested_formats"]))

    def test_noncanonical_transfer_bytes_rejected(self):
        raw = (json.dumps(transfer(), indent=2) + "\n").encode()
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(PublisherArtifactTransferError):
                process_artifact_transfer(raw, Path(td))

    def test_authority_expansion_rejected(self):
        value = transfer()
        value["publication_authorized"] = True
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(PublisherArtifactTransferError):
                process_artifact_transfer(canonical_json(value).encode(), Path(td))

    def test_mir_roundtrip_binding_is_preserved_in_exact_artifact_return(self):
        raw = canonical_json(transfer_with_roundtrip_binding()).encode()
        with tempfile.TemporaryDirectory() as td:
            result, returned = process_artifact_transfer(raw, Path(td))
        parsed = verify_artifact_return(returned)
        binding = parsed["roundtrip_binding"]
        self.assertEqual(parsed, result)
        self.assertEqual("stegverse.publisher.artifact-return/v1", parsed["schema"])
        self.assertEqual(MANIFEST_HASH, binding["manifest_hash"])
        self.assertEqual(RESPONSE_TO, binding["response_to"])
        self.assertEqual(RETAINED_PACKET_HASH, binding["retained_packet_sha256"])
        self.assertTrue(binding["publisher_transition_observed"])
        self.assertEqual(parsed["source_export_id"], binding["publisher_return_source_export_id"])
        self.assertEqual(parsed["source_export_sha256"], binding["publisher_return_source_export_sha256"])
        self.assertEqual(parsed["generation_id"], binding["publisher_return_generation_id"])
        self.assertEqual(parsed["manifest"]["manifest_sha256"], binding["publisher_artifact_manifest_sha256"])
        self.assertFalse(binding["sdk_return_binding_observed"])
        self.assertFalse(binding["final_stegverse_side_egress_transition_observed"])
        self.assertFalse(binding["interlock_intr_egress_observed"])
        self.assertFalse(binding["far_side_transition_observed"])
        self.assertFalse(binding["communication_complete"])
        self.assertEqual("NONE", binding["authority_effect"])

    def test_mir_roundtrip_transfer_rejects_when_publisher_not_required(self):
        capsule = completion_capsule(publisher_required=False)
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(PublisherArtifactTransferError, "does not require Publisher"):
                process_artifact_transfer(
                    canonical_json(
                        transfer_with_roundtrip_binding(
                            downstream_completion_capsule=capsule,
                            completion_hash=capsule["completion_hash"],
                        )
                    ).encode(),
                    Path(td),
                )

    def test_mir_roundtrip_transfer_rejects_completion_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(PublisherArtifactTransferError, "completion hash mismatch"):
                process_artifact_transfer(
                    canonical_json(transfer_with_roundtrip_binding(completion_hash="sha256:" + "0" * 64)).encode(),
                    Path(td),
                )

    def test_mir_roundtrip_return_rejects_downstream_promotion(self):
        raw = canonical_json(transfer_with_roundtrip_binding()).encode()
        with tempfile.TemporaryDirectory() as td:
            _, returned = process_artifact_transfer(raw, Path(td))
        parsed = json.loads(returned.decode())
        parsed["roundtrip_binding"]["sdk_return_binding_observed"] = True
        with self.assertRaisesRegex(PublisherArtifactTransferError, "sdk_return_binding_observed"):
            verify_artifact_return(canonical_json(parsed).encode())


if __name__ == "__main__":
    unittest.main()
