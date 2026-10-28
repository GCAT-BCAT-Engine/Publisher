# Carried in-repo, verbatim from GCAT-BCAT-Engine/core-full@76227b0:src/stegverse_core_full/monitoring/stegdb.py (sha256 c3f79c60518ed1fad392d04c0a64edbbe76469ff4fcb5ec8980296e5ba856431).
# Edits: none.
"""
StegDB monitoring interface.
Lightweight hook for StegDB pre-transition checks.
"""

from typing import Dict, Any, Optional, Protocol, runtime_checkable


@runtime_checkable
class StegDBInterface(Protocol):
    """Protocol for StegDB implementations."""
    def check(self, receipt_id: str) -> str: ...  # "cleared" | "pending" | "blocked"
    def permit(self, receipt_id: str) -> bool: ...
    def log(self, receipt_id: str, event: Dict[str, Any]) -> bool: ...


class StegDBMonitor:
    """
    Lightweight StegDB monitor for Core-Full.
    Can be backed by a real StegDB instance or a mock for testing.
    """

    def __init__(self, stegdb_impl: Optional[StegDBInterface] = None):
        self.stegdb = stegdb_impl
        self._local_cache: Dict[str, str] = {}

    def check(self, receipt_id: str) -> str:
        """Check if receipt_id is cleared by StegDB."""
        if receipt_id in self._local_cache:
            return self._local_cache[receipt_id]

        if self.stegdb:
            status = self.stegdb.check(receipt_id)
            self._local_cache[receipt_id] = status
            return status

        # Default: no StegDB configured, auto-clear (dev mode)
        return "cleared"

    def permit(self, receipt_id: str) -> bool:
        """Explicitly permit a receipt after monitoring."""
        if self.stegdb:
            return self.stegdb.permit(receipt_id)
        self._local_cache[receipt_id] = "cleared"
        return True

    def log(self, receipt_id: str, event: Dict[str, Any]) -> bool:
        """Log an event to StegDB."""
        if self.stegdb:
            return self.stegdb.log(receipt_id, event)
        return True


def main():
    # Demo with no backend (dev mode)
    monitor = StegDBMonitor()
    print(f"Check (no backend): {monitor.check('test-receipt-001')}")
    print(f"Permit: {monitor.permit('test-receipt-001')}")


if __name__ == "__main__":
    main()
