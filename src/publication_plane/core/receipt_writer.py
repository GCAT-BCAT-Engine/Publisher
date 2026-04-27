"""
Deterministic publication receipt writer.
Integrates with stegverse-core-lite for seeded, reproducible receipt IDs.
"""

from pathlib import Path
import json
from typing import Dict, Any, Optional

from stegverse_core_lite.interfaces.protocols import ReceiptIDProvider
from stegverse_core_lite.receipt.id import DeterministicReceiptID


class PublicationReceiptWriter:
    """
    Writes deterministic, notarized receipts for all publication events.
    Receipt IDs are derived from content hash + seed — fully reproducible.
    """

    def __init__(
        self,
        receipt_provider: Optional[ReceiptIDProvider] = None,
        seed: Optional[str] = None,
        output_dir: str = "receipts"
    ):
        self.receipt_provider = receipt_provider or DeterministicReceiptID()
        self.seed = seed or "publisher-default-seed"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write(
        self,
        gate_result: str,           # "ALLOW" | "DENY" | "FAIL_CLOSED"
        confidence: float,
        evidence: Dict[str, Any],
        module: str,
        destination: str,
        status: str = "pending_notarization"
    ) -> Path:
        """
        Generate and write a deterministic publication receipt.
        """
        from datetime import datetime, timezone

        timestamp = datetime.now(timezone.utc).isoformat()

        payload = {
            "schema_version": "1.0.0",
            "module": module,
            "gate_result": gate_result,
            "confidence": confidence,
            "evidence": evidence,
            "destination": destination,
            "status": status,
            "timestamp": timestamp,
            "seed": self.seed,
        }

        # Deterministic ID via injected provider
        receipt_id = self.receipt_provider.derive(payload, self.seed)
        payload["receipt_id"] = receipt_id

        # Write
        filepath = self.output_dir / f"{receipt_id}.json"
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        return filepath

    def verify(self, receipt_path: Path) -> bool:
        """
        Verify a receipt's integrity by re-deriving its ID.
        """
        data = json.loads(receipt_path.read_text(encoding="utf-8"))
        stored_id = data.pop("receipt_id", None)
        derived_id = self.receipt_provider.derive(data, data.get("seed", self.seed))
        return stored_id == derived_id


def main():
    # Demo usage
    writer = PublicationReceiptWriter(seed="demo-run-001")

    receipt = writer.write(
        gate_result="ALLOW",
        confidence=0.947,
        evidence={"test_suite": "demo-suite-runner", "passes": 3, "deterministic": True},
        module="publication_plane.core.receipt_writer",
        destination="GCAT-BCAT-Engine/Publisher",
        status="published"
    )

    print(f"Receipt written: {receipt}")
    print(f"Verified: {writer.verify(receipt)}")


if __name__ == "__main__":
    main()
