"""
Publisher-specific badge generation wrapper.
"""

from typing import Dict, Any

from stegverse_core_addons.badge.replication import ReplicationBadgeGenerator


class PublisherBadgeGenerator:
    """
    Generates badges for Publisher-tracked publications.
    Thin wrapper around core-addons badge generator.
    """

    def __init__(self, generator: ReplicationBadgeGenerator = None):
        self.generator = generator or ReplicationBadgeGenerator()

    def generate_for_publication(
        self,
        receipt_id: str,
        seed: str,
        confidence: float,
        passes: int = 1
    ) -> Dict[str, Any]:
        """Generate badge for a publication."""
        badge = self.generator.generate(
            receipt_id=receipt_id,
            seed=seed,
            passes=passes,
            confidence=confidence,
            deterministic=True,
        )

        return {
            "badge_id": badge.badge_id,
            "svg_path": f"badges/{badge.badge_id}.svg",
            "confidence": badge.confidence,
            "deterministic": badge.deterministic,
        }


def main():
    gen = PublisherBadgeGenerator()
    result = gen.generate_for_publication("rcp-001", "seed", 0.95, 3)
    print(f"Badge: {result['badge_id']}")
    print(f"SVG: {result['svg_path']}")


if __name__ == "__main__":
    main()
