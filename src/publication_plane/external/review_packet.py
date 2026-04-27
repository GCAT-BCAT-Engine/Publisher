"""
Open review packet builder.
Assembles review-ready packages for external review platforms.
"""

import json
from pathlib import Path
from typing import Dict, Any, List

from stegverse_core_lite.receipt.id import DeterministicReceiptID


class ReviewPacketBuilder:
    """
    Builds review packets for open review platforms (arXiv, OpenReview, etc.).
    """

    def __init__(self, output_dir: str = "review_packets"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build(
        self,
        title: str,
        abstract: str,
        sections: List[Dict[str, Any]],
        figures: List[Dict[str, Any]],
        evidence: Dict[str, Any],
        seed: str = "default"
    ) -> Path:
        """
        Build a review packet with all necessary materials.
        """
        packet = {
            "title": title,
            "abstract": abstract,
            "sections": sections,
            "figures": figures,
            "evidence": evidence,
            "schema": "stegverse-review-v1",
        }

        # Receipt the packet itself
        receipt_id = DeterministicReceiptID().derive(packet, seed)
        packet["receipt_id"] = receipt_id
        packet["seed"] = seed

        path = self.output_dir / f"{receipt_id}_review_packet.json"
        path.write_text(json.dumps(packet, indent=2), encoding="utf-8")

        return path


def main():
    builder = ReviewPacketBuilder()

    path = builder.build(
        title="GCAT/BCAT Invariant Verification",
        abstract="We verify the GCAT/BCAT invariant...",
        sections=[{"heading": "Introduction", "text": "..."}],
        figures=[{"id": "fig1", "caption": "Proof diagram"}],
        evidence={"appendix": "evidence/rcp-001_evidence.json"},
        seed="review-001"
    )

    print(f"Review packet: {path}")


if __name__ == "__main__":
    main()
