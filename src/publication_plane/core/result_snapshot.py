"""
Immutable result snapshot capture.
Freezes publication-bound data for audit and verification.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

from stegverse_core_lite.hash.deterministic import DeterministicHash


class ResultSnapshot:
    """
    Captures an immutable snapshot of results before publication.
    Includes content hash for integrity verification.
    """

    def __init__(self, output_dir: str = "evidence"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def capture(
        self,
        data: Dict[str, Any],
        source: str,
        seed: str = "default"
    ) -> Path:
        """
        Capture and freeze a result snapshot.
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        # Canonical hash
        canonical = json.dumps(data, sort_keys=True, ensure_ascii=True)
        content_hash = DeterministicHash.hash(canonical, seed)

        snapshot = {
            "schema_version": "1.0.0",
            "source": source,
            "captured_at": timestamp,
            "content_hash": content_hash,
            "seed": seed,
            "data": data,
        }

        # Filename includes hash prefix for quick lookup
        filename = f"{content_hash[:16]}_{source}.json"
        filepath = self.output_dir / filename
        filepath.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

        return filepath

    def verify(self, snapshot_path: Path) -> bool:
        """Verify snapshot integrity by re-hashing."""
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        stored_hash = snapshot["content_hash"]
        seed = snapshot["seed"]

        canonical = json.dumps(snapshot["data"], sort_keys=True, ensure_ascii=True)
        derived_hash = DeterministicHash.hash(canonical, seed)

        return stored_hash == derived_hash


def main():
    snapshot = ResultSnapshot()

    data = {
        "gate_result": "ALLOW",
        "confidence": 0.947,
        "test_suite": "demo-suite-runner",
        "passes": 3,
    }

    path = snapshot.capture(data, source="sandbox", seed="snapshot-demo-001")
    print(f"Snapshot: {path}")
    print(f"Verified: {snapshot.verify(path)}")


if __name__ == "__main__":
    main()
