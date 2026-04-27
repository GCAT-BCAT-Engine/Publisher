"""
Evidence and claim-to-figure linking.
Builds verifiable evidence trails for publications.
"""

import json
from pathlib import Path
from typing import Dict, Any, List

from stegverse_core_lite.hash.deterministic import DeterministicHash


class EvidenceBuilder:
    """
    Builds evidence appendices linking claims to figures, data, and receipts.
    """

    def __init__(self, output_dir: str = "evidence"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_appendix(
        self,
        claims: List[Dict[str, Any]],
        figures: List[Dict[str, Any]],
        receipt_id: str,
        seed: str = "default"
    ) -> Path:
        """
        Build an evidence appendix linking claims to figures.
        """
        # Link claims to figures
        linked = []
        for claim in claims:
            figure_refs = claim.get("figure_refs", [])
            linked_figures = [f for f in figures if f["id"] in figure_refs]

            linked.append({
                "claim_id": claim["id"],
                "claim_text": claim["text"],
                "figures": linked_figures,
                "confidence": claim.get("confidence", 0.0),
            })

        # Hash the entire appendix
        canonical = json.dumps(linked, sort_keys=True)
        appendix_hash = DeterministicHash.hash(canonical, seed)

        appendix = {
            "schema_version": "1.0.0",
            "receipt_id": receipt_id,
            "appendix_hash": appendix_hash,
            "seed": seed,
            "claims": linked,
            "figure_count": len(figures),
        }

        path = self.output_dir / f"{receipt_id}_evidence.json"
        path.write_text(json.dumps(appendix, indent=2), encoding="utf-8")

        return path

    def verify_appendix(self, appendix_path: Path) -> bool:
        """Verify evidence appendix integrity."""
        data = json.loads(appendix_path.read_text(encoding="utf-8"))
        stored_hash = data["appendix_hash"]
        seed = data["seed"]

        canonical = json.dumps(data["claims"], sort_keys=True)
        derived = DeterministicHash.hash(canonical, seed)

        return stored_hash == derived


def main():
    builder = EvidenceBuilder()

    claims = [
        {"id": "c1", "text": "Invariant holds", "figure_refs": ["fig1"], "confidence": 0.95},
        {"id": "c2", "text": "Receipts verify", "figure_refs": ["fig2"], "confidence": 0.91},
    ]

    figures = [
        {"id": "fig1", "caption": "Invariant proof", "path": "figures/fig1.png"},
        {"id": "fig2", "caption": "Receipt verification", "path": "figures/fig2.png"},
    ]

    path = builder.build_appendix(claims, figures, "rcp-evidence-001", "seed-001")
    print(f"Evidence: {path}")
    print(f"Verified: {builder.verify_appendix(path)}")


if __name__ == "__main__":
    main()
