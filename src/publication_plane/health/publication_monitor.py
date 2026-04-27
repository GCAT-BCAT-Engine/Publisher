"""
Publication pipeline health monitoring.
Tracks the health of all publication_plane components.
"""

from typing import Dict, Any, List
from datetime import datetime, timezone

from stegverse_core_addons.analytics.telemetry import TelemetryCollector, HealthMetrics


class PublicationHealthMonitor:
    """
    Monitors the health of the publication pipeline.
    Collects metrics from all publication_plane modules.
    """

    def __init__(self):
        self.collectors: Dict[str, TelemetryCollector] = {}

    def register_component(self, name: str):
        """Register a component for health tracking."""
        self.collectors[name] = TelemetryCollector(name)

    def record(
        self,
        component: str,
        version: str,
        requests_total: int,
        requests_success: int,
        avg_confidence: float,
        last_receipt_id: str
    ):
        """Record metrics for a component."""
        if component not in self.collectors:
            self.register_component(component)

        metrics = HealthMetrics(
            component=component,
            version=version,
            uptime_seconds=0.0,  # Would be calculated in production
            requests_total=requests_total,
            requests_success=requests_success,
            requests_fail=requests_total - requests_success,
            avg_confidence=avg_confidence,
            last_receipt_id=last_receipt_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        self.collectors[component].record(metrics)

    def get_health_report(self) -> Dict[str, Any]:
        """Generate a health report for all components."""
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {},
            "overall_status": "healthy",
        }

        for name, collector in self.collectors.items():
            latest = collector.get_latest()
            success_rate = latest.requests_success / max(latest.requests_total, 1)

            status = "healthy"
            if success_rate < 0.9:
                status = "degraded"
            if success_rate < 0.5:
                status = "critical"

            report["components"][name] = {
                "status": status,
                "success_rate": success_rate,
                "avg_confidence": latest.avg_confidence,
                "last_receipt": latest.last_receipt_id,
                "version": latest.version,
            }

            if status == "critical":
                report["overall_status"] = "critical"
            elif status == "degraded" and report["overall_status"] != "critical":
                report["overall_status"] = "degraded"

        return report


def main():
    monitor = PublicationHealthMonitor()

    monitor.record("receipt_writer", "1.0.0", 100, 98, 0.94, "rcp-001")
    monitor.record("publication_gate", "1.0.0", 100, 95, 0.91, "rcp-002")
    monitor.record("demo_sync", "1.0.0", 50, 40, 0.85, "rcp-003")

    report = monitor.get_health_report()
    print(f"Overall: {report['overall_status']}")
    for comp, data in report["components"].items():
        print(f"  {comp}: {data['status']} ({data['success_rate']:.0%} success)")


if __name__ == "__main__":
    main()
