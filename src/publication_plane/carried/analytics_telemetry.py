# Carried in-repo, verbatim from GCAT-BCAT-Engine/core-addons@29a74ef:stegverse_core_addons/analytics/telemetry.py (sha256 05397b9c3f0615a219109ad7676d8365961e22ab52cd2c04b7f80b7800db1c8b).
# Edits: none.
# Edit: 1 upload-damaged string literal(s) repaired: a literal line break inside a string restored to the \n escape it
#   replaced (the source file does not parse; GCAT-BCAT-Engine/core-addons 'Add files via upload'). No other change.
"""
Telemetry and health metrics for StegVerse components.
Lightweight, privacy-respecting analytics.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List
from dataclasses import dataclass, asdict


@dataclass
class HealthMetrics:
    component: str
    version: str
    uptime_seconds: float
    requests_total: int
    requests_success: int
    requests_fail: int
    avg_confidence: float
    last_receipt_id: str
    timestamp: str


class TelemetryCollector:
    """
    Collects health metrics from StegVerse components.
    Stores locally; optionally syncs to analytics backend.
    """

    def __init__(self, component: str, store_dir: str = "telemetry"):
        self.component = component
        self.store = Path(store_dir)
        self.store.mkdir(parents=True, exist_ok=True)
        self._metrics_file = self.store / f"{component}_metrics.jsonl"

    def record(self, metrics: HealthMetrics):
        """Record a metrics snapshot."""
        with open(self._metrics_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(metrics), sort_keys=True) + "\n")

    def get_latest(self) -> HealthMetrics:
        """Get the most recent metrics snapshot."""
        if not self._metrics_file.exists():
            return self._default_metrics()

        with open(self._metrics_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if not lines:
                return self._default_metrics()
            latest = json.loads(lines[-1])
            return HealthMetrics(**latest)

    def get_history(self, n: int = 10) -> List[HealthMetrics]:
        """Get last N metrics snapshots."""
        if not self._metrics_file.exists():
            return []

        with open(self._metrics_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return [HealthMetrics(**json.loads(line)) for line in lines[-n:]]

    def _default_metrics(self) -> HealthMetrics:
        return HealthMetrics(
            component=self.component,
            version="unknown",
            uptime_seconds=0.0,
            requests_total=0,
            requests_success=0,
            requests_fail=0,
            avg_confidence=0.0,
            last_receipt_id="",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


def main():
    collector = TelemetryCollector("publisher")

    metrics = HealthMetrics(
        component="publisher",
        version="1.0.0",
        uptime_seconds=3600.0,
        requests_total=150,
        requests_success=142,
        requests_fail=8,
        avg_confidence=0.91,
        last_receipt_id="abc123",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    collector.record(metrics)
    latest = collector.get_latest()
    print(f"Latest: {latest.component} v{latest.version} — {latest.requests_success}/{latest.requests_total} success")


if __name__ == "__main__":
    main()
