# Carried in-repo, verbatim from GCAT-BCAT-Engine/core-full@76227b0:src/stegverse_core_full/notary/core.py (sha256 fd1f6218a76536780203e148b4b3005d0d78d65371f1e245f203c4c833ba2e56).
# Edits: none.
"""
Pre-transition notarization.
No state transition is permitted without notarized clearance.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class NotarizationRecord:
    notarization_id: str
    receipt_id: str
    evidence_hash: str
    destination: str
    release_type: str
    timestamp: str
    status: str
    transition_permitted: bool
    cleared_at: Optional[str] = None


class ResearchReleaseNotary:
    """
    Notarizes research releases before they enter any publication channel.
    Creates an immutable notarization record linking receipt, evidence, and destination.
    """

    def __init__(self, notary_store: str = "notary_store"):
        self.store = Path(notary_store)
        self.store.mkdir(parents=True, exist_ok=True)

    def notarize(
        self,
        receipt_id: str,
        evidence_hash: str,
        destination: str,
        release_type: str = "research"
    ) -> NotarizationRecord:
        """
        Create a notarization seal. Returns a record that must be
        checked by StegDB before any transition proceeds.
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        notarization_id = self._derive_id(receipt_id, evidence_hash, timestamp)

        record = NotarizationRecord(
            notarization_id=notarization_id,
            receipt_id=receipt_id,
            evidence_hash=evidence_hash,
            destination=destination,
            release_type=release_type,
            timestamp=timestamp,
            status="notarized",
            transition_permitted=False,  # StegDB must flip this
        )

        self._write(record)
        return record

    def permit_transition(self, notarization_id: str) -> bool:
        """
        StegDB calls this after monitoring confirms integrity.
        """
        record = self._read(notarization_id)
        if not record:
            return False

        record.transition_permitted = True
        record.cleared_at = datetime.now(timezone.utc).isoformat()
        record.status = "cleared"

        self._write(record)
        return True

    def get_record(self, notarization_id: str) -> Optional[NotarizationRecord]:
        return self._read(notarization_id)

    def _derive_id(self, receipt_id: str, evidence_hash: str, timestamp: str) -> str:
        composite = f"{receipt_id}::{evidence_hash}::{timestamp}"
        return hashlib.sha256(composite.encode()).hexdigest()[:32]

    def _write(self, record: NotarizationRecord):
        path = self.store / f"{record.notarization_id}.json"
        path.write_text(json.dumps(asdict(record), indent=2), encoding="utf-8")

    def _read(self, notarization_id: str) -> Optional[NotarizationRecord]:
        path = self.store / f"{notarization_id}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return NotarizationRecord(**data)


def main():
    notary = ResearchReleaseNotary()

    record = notary.notarize(
        receipt_id="abc123def456",
        evidence_hash="sha256:deadbeef",
        destination="GCAT-BCAT-Engine/Publisher",
        release_type="demo"
    )

    print(f"Notarized: {record.notarization_id}")
    print(f"Transition permitted? {record.transition_permitted}")

    # Simulate StegDB clearance
    notary.permit_transition(record.notarization_id)
    updated = notary.get_record(record.notarization_id)
    print(f"After clearance: {updated.transition_permitted}")
    print(f"Cleared at: {updated.cleared_at}")


if __name__ == "__main__":
    main()
