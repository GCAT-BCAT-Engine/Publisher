"""
Demo surface synchronization.
Publishes demo artifacts to live surfaces and keeps them current.
"""

from typing import Dict, Any, List
from pathlib import Path

from stegverse_core_addons.badge.replication import ReplicationBadgeGenerator


class DemoSurfaceSync:
    """
    Syncs demo artifacts to publication surfaces.
    Generates badges, updates pointers, and maintains sync state.
    """

    def __init__(self, badge_generator: ReplicationBadgeGenerator = None):
        self.badge_generator = badge_generator or ReplicationBadgeGenerator()
        self._sync_state: Dict[str, Any] = {}

    def publish_demo(
        self,
        receipt_id: str,
        seed: str,
        demo_data: Dict[str, Any],
        surfaces: List[str] = None
    ) -> Dict[str, Any]:
        """
        Publish a demo result to configured surfaces.
        """
        surfaces = surfaces or ["github_releases", "demo_page"]

        # Generate badge
        badge = self.badge_generator.generate(
            receipt_id=receipt_id,
            seed=seed,
            passes=demo_data.get("passes", 0),
            confidence=demo_data.get("confidence", 0.0),
            deterministic=demo_data.get("deterministic", False),
        )

        result = {
            "receipt_id": receipt_id,
            "seed": seed,
            "surfaces": surfaces,
            "badge_id": badge.badge_id,
            "published_at": badge.generated_at,
            "status": "published",
        }

        self._sync_state[receipt_id] = result
        return result

    def get_sync_state(self, receipt_id: str) -> Dict[str, Any]:
        return self._sync_state.get(receipt_id, {})


def main():
    sync = DemoSurfaceSync()

    result = sync.publish_demo(
        receipt_id="rcp-demo-001",
        seed="run-001",
        demo_data={"passes": 3, "confidence": 0.947, "deterministic": True},
        surfaces=["github_releases", "demo_page", "social_media"]
    )

    print(f"Published to: {result['surfaces']}")
    print(f"Badge: {result['badge_id']}")


if __name__ == "__main__":
    main()
