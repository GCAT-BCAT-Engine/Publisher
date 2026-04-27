"""
Publication-specific notary wrapper.
Bridges core-full notary with publication workflows.
"""

from typing import Dict, Any

from stegverse_core_full.notary.core import ResearchReleaseNotary
from stegverse_core_lite.hash.deterministic import DeterministicHash


class PublicationNotary:
    """
    Notarizes publication-bound artifacts before release.
    Wraps core-full notary with publication-specific hashing.
    """

    def __init__(self, notary: ResearchReleaseNotary = None):
        self.notary = notary or ResearchReleaseNotary()

    def notarize_artifact(
        self,
        artifact_data: Dict[str, Any],
        destination: str,
        release_type: str = "demo"
    ) -> Dict[str, Any]:
        """
        Notarize a publication artifact.
        """
        # Hash the artifact content
        canonical = str(sorted(artifact_data.items()))
        evidence_hash = DeterministicHash.hash(canonical, "artifact")

        # Generate receipt ID for the artifact
        from stegverse_core_lite.receipt.id import DeterministicReceiptID
        receipt_id = DeterministicReceiptID().derive(artifact_data, "artifact-seed")

        # Notarize via core-full
        record = self.notary.notarize(
            receipt_id=receipt_id,
            evidence_hash=evidence_hash,
            destination=destination,
            release_type=release_type,
        )

        return {
            "notarization_id": record.notarization_id,
            "receipt_id": receipt_id,
            "evidence_hash": evidence_hash,
            "destination": destination,
            "status": record.status,
            "transition_permitted": record.transition_permitted,
        }

    def clear_for_publication(self, notarization_id: str) -> bool:
        """Permit transition after StegDB clearance."""
        return self.notary.permit_transition(notarization_id)


def main():
    notary = PublicationNotary()

    artifact = {
        "type": "demo_result",
        "gate_result": "ALLOW",
        "confidence": 0.947,
        "suite": "demo-suite-runner",
    }

    result = notary.notarize_artifact(artifact, "GCAT-BCAT-Engine/Publisher", "demo")
    print(f"Notarized: {result['notarization_id']}")
    print(f"Permitted: {result['transition_permitted']}")

    notary.clear_for_publication(result["notarization_id"])
    updated = notary.notary.get_record(result["notarization_id"])
    print(f"After clearance: {updated.transition_permitted}")


if __name__ == "__main__":
    main()
